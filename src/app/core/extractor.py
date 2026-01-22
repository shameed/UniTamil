import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import multiprocessing
import time
from typing import Callable, Iterator, Dict
from ..utils.logger import logger
from .dependency_checker import DependencyChecker
from .ocr_worker import run_ocr

# Configure pytesseract path if needed
# In a real app, we might pass the path from DependencyChecker instance

class PDFExtractor:
    def __init__(self, tesseract_path: str = None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
    def process_pdf(self, pdf_path: str, should_stop: Callable[[], bool] = None) -> Iterator[Dict]:
        """
        Process a single PDF file and yield page data one by one.
        Yields: {'page_num': int, 'text': str, 'method': str, 'total_pages': int}
        
        Args:
            pdf_path: Path to PDF file
            should_stop: Callable that returns True if processing should stop
        """
        try:
            doc = fitz.open(pdf_path)
            logger.info(f"Processing PDF: {pdf_path} ({len(doc)} pages)")
            total_pages = len(doc)
            
            for page_num, page in enumerate(doc, 1):
                # Check stop BEFORE processing page
                if should_stop and should_stop():
                    logger.info(f"Stop requested before page {page_num}")
                    doc.close()
                    return
                    
                logger.debug(f"Processing page {page_num}...")
                
                # 1. Try text extraction first (fast)
                text = page.get_text()
                
                # 2. Heuristic: Check if text is sufficient
                use_ocr = len(text.strip()) < 50
                method = "text_extraction"
                
                if use_ocr:
                    logger.debug(f"Page {page_num}: Low text, attempting OCR...")
                    
                    # Check stop BEFORE expensive OCR
                    if should_stop and should_stop():
                        logger.info(f"Stop requested before OCR on page {page_num}")
                        doc.close()
                        return
                    
                    try:
                        # Render page to image bytes
                        pix = page.get_pixmap(dpi=300)
                        img_bytes = pix.tobytes("png")
                        
                        # Run OCR in subprocess (killable)
                        text, ocr_success = self._run_ocr_subprocess(img_bytes, should_stop)
                        
                        if not ocr_success:
                            # Stop was requested during OCR
                            logger.info(f"OCR interrupted on page {page_num}")
                            doc.close()
                            return
                            
                        method = "ocr"
                        logger.debug(f"Page {page_num}: OCR completed.")
                        
                    except Exception as e:
                        logger.warning(f"Page {page_num}: OCR failed: {e}")
                        text = ""
                        method = "skipped_ocr_failed"
                
                # Check for unreadable text
                if not text.strip():
                     logger.warning(f"Page {page_num}: No readable text found. Skipping.")
                     method = "skipped_no_text"
                
                yield {
                    "page_num": page_num,
                    "text": text,
                    "method": method,
                    "total_pages": total_pages
                }
                
            doc.close()
            
        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise e

    def _run_ocr_subprocess(self, img_bytes: bytes, should_stop: Callable[[], bool] = None, poll_interval: float = 0.1) -> tuple:
        """
        Run OCR in a subprocess using stdin/stdout.
        
        Returns:
            (text, success): text result and whether it completed (vs was killed)
        """
        import subprocess
        import sys
        import base64
        
        # Prepare input
        encoded_img = base64.b64encode(img_bytes).decode('ascii')
        
        # Prepare command: [executable, "--ocr-worker"]
        # In frozen app, sys.executable is the exe. In dev, it's python.exe.
        # If in dev, we need to pass the script path too, but our main.py handles the flag.
        # However, running "python main.py --ocr-worker" is required in dev.
        # We can detect if frozen.
        
        cmd = [sys.executable]
        if not getattr(sys, 'frozen', False):
            # Development mode: python src/main.py --ocr-worker
            # We assume we are running from root or src is in path
            # Actually simplest is to point to src/main.py
            import os
            # Get path to main.py. It's usually known relative to this file?
            # Safer: current main script
            main_script = sys.modules['__main__'].__file__
            if main_script: 
                 cmd.append(main_script)
            else:
                 # Fallback
                 cmd.append("src/main.py")
        
        cmd.append("--ocr-worker")
        
        # Startup info to hide window on Windows
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            # Also use creationflags for extra insurance against console popping up
            creationflags = 0x08000000 # CREATE_NO_WINDOW

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True, # We'll send base64 string
                startupinfo=startupinfo,
                creationflags=creationflags if sys.platform == 'win32' else 0,
                encoding='utf-8' # Ensure text pipes are utf-8
            )
            
            # Write input non-blocking? No, just write.
            # But we want to kill it if it hangs.
            # subprocess.communicate supports timeout, which is great, but we want to check `should_stop`.
            
            # We can't use communicate if we want granular stopping during the "write" phase easily,
            # but write is fast. The wait for output is slow.
            
            # Proper strategy: verify process started, write data, then wait for result with polling.
            
            # Since communicate blocks, we use a loop with Popen.poll() or similar?
            # Actually, `communicate` with timeout is the best way to leverage threading for I/O.
            # But we can't share the "should_stop" cleanly with communicate's internal wait.
            
            # Hybrid approach: 
            # 1. Write input in a separate thread? Or just write it (it's small, <10MB usually).
            process.stdin.write(encoded_img)
            process.stdin.close() # Signal EOF
            
            # 2. Wait for finish
            while process.poll() is None:
                if should_stop and should_stop():
                    logger.info("Killing OCR subprocess (Popen)...")
                    process.terminate()
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    return ("", False)
                time.sleep(poll_interval)
                
            # 3. Get output
            stdout_content = process.stdout.read()
            stderr_content = process.stderr.read()
            process.stdout.close()
            process.stderr.close()
            
            if process.returncode != 0:
                logger.warning(f"OCR Subprocess failed code {process.returncode}: {stderr_content}")
                return ("", True) # Treated as empty text (failure), but "not skipped/killed"
                
            return (stdout_content, True)

        except Exception as e:
            logger.error(f"Subprocess launch failed: {e}")
            return ("", True)

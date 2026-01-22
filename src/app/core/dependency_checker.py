import shutil
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.logger import logger

class DependencyChecker:
    def __init__(self):
        self.tesseract_path: Optional[str] = None
        self.tesseract_version: Optional[str] = None
        self.languages: List[str] = []
        
    def check_tesseract(self) -> bool:
        """Checks if Tesseract is installed and available in PATH or common locations."""
        # 1. Check PATH
        self.tesseract_path = shutil.which("tesseract")
        
        # 2. Check common Windows paths
        if not self.tesseract_path:
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                Path.home() / "AppData/Local/Tesseract-OCR/tesseract.exe"
            ]
            for p in common_paths:
                if Path(p).exists():
                    self.tesseract_path = str(p)
                    break
                    
        if self.tesseract_path:
            logger.info(f"Tesseract found at: {self.tesseract_path}")
            return True
        else:
            logger.error("Tesseract not found.")
            return False

    def check_languages(self) -> Dict[str, bool]:
        """Checks for required language packs (tam, eng)."""
        if not self.tesseract_path:
            return {"eng": False, "tam": False}
            
        try:
            # Prepare startupinfo for window hiding on Windows
            startupinfo = None
            creationflags = 0
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = 0x08000000 # CREATE_NO_WINDOW

            # Query languages
            result = subprocess.run(
                [self.tesseract_path, "--list-langs"],
                capture_output=True,
                text=True,
                check=True,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            output = result.stdout.lower()
            
            # Helper to check lang in output
            # Tesseract output format varies, usually just a list of codes
            installed_langs = [line.strip() for line in output.splitlines()]
            
            status = {
                "eng": any("eng" in l for l in installed_langs),
                "tam": any("tam" in l for l in installed_langs)
            }
            
            logger.info(f"Language Pack Status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Failed to check languages: {e}")
            return {"eng": False, "tam": False}

    def get_status(self) -> Dict[str, any]:
        """Returns full dependency status."""
        tess_ok = self.check_tesseract()
        lang_status = self.check_languages() if tess_ok else {"eng": False, "tam": False}
        
        return {
            "tesseract_found": tess_ok,
            "tesseract_path": self.tesseract_path,
            "languages": lang_status,
            "ready": tess_ok and lang_status["eng"] and lang_status["tam"]
        }

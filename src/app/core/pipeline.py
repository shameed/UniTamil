from pathlib import Path
from typing import List, Callable
import json
from .extractor import PDFExtractor
from .converter import LegacyConverter
from .normalizer import Normalizer
from ..utils.logger import logger

class ProcessingPipeline:
    def __init__(self, tesseract_path: str = None):
        self.extractor = PDFExtractor(tesseract_path)
        self.converter = LegacyConverter()
        self.normalizer = Normalizer()
        
    def process_file(self, 
                     input_path: str, 
                     output_dir: str, 
                     progress_callback: Callable[[float, str], None] = None,
                     should_stop: Callable[[], bool] = None) -> bool: # Added should_stop arg
        """
        Full processing pipeline for a single PDF.
        """
        try:
            input_file = Path(input_path)
            # Create output directory for this PDF
            pdf_out_dir = Path(output_dir) / input_file.stem
            pdf_out_dir.mkdir(parents=True, exist_ok=True)
            pages_dir = pdf_out_dir / "pages"
            pages_dir.mkdir(exist_ok=True)
            
            if progress_callback:
                progress_callback(0.1, f"Starting extraction: {input_file.name}")
                
            # 1. Iterate over generator
            full_text = []
             # Need to track processed pages for metadata
            processed_count = 0
            total_pages = 0
            
            for page_data in self.extractor.process_pdf(str(input_file), should_stop=should_stop):
                # 2. Check Stop Signal
                if should_stop and should_stop():
                    logger.info(f"Stopping processing for {input_file.name} (User Request)")
                    if progress_callback:
                        progress_callback(0.0, "Stopped by User")
                    return False
                
                page_num = page_data['page_num']
                total_pages = page_data.get('total_pages', 0)
                
                # Calculate progress for this page (used by all branches below)
                if total_pages > 0:
                    prog = 0.2 + (0.7 * (page_num / total_pages))
                else:
                    prog = 0.5
                
                # 3. Resume Logic: Check if exists
                page_md_path = pages_dir / f"page_{page_num}.md"
                if page_md_path.exists():
                     if progress_callback:
                         progress_callback(prog, f"Page {page_num} exists, skipping (Resume).")
                     # Read content to append to full_text for combined MD
                     with open(page_md_path, "r", encoding="utf-8") as f:
                         # Skip header "# Page N"
                         content = f.read().split("\n\n", 1)[-1] 
                         full_text.append(content)
                     processed_count += 1
                     continue

                if progress_callback:
                    progress_callback(prog, f"Processing page {page_num}/{total_pages}...")
                
                # 4. Handle status
                if "skipped" in page_data["method"]:
                    if progress_callback:
                        progress_callback(prog, f"Warning: Page {page_num} skipped ({page_data['method']})")
                    logger.warning(f"Skipping Page {page_num} due to {page_data['method']}")
                    continue # Skip processing this page
                
                raw_text = page_data["text"]
                
                # 5. Legacy Conversion
                converted_text = self.converter.convert(raw_text)
                
                # 6. Normalization
                final_text = self.normalizer.normalize(converted_text)
                
                # 7. Save Page Markdown
                self._write_markdown(page_md_path, final_text, page_num)
                
                full_text.append(final_text)
                processed_count += 1
            
            # 8. Save combined Markdown
            combined_md_path = pdf_out_dir / "extracted.md"
            self._write_combined_markdown(combined_md_path, full_text)
            
            # 9. Metadata
            metadata = {
                "original_filename": input_file.name,
                "total_pages": total_pages,
                "processed_pages": processed_count
            }
            with open(pdf_out_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
                
            if progress_callback:
                progress_callback(1.0, "Complete")
                
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed for {input_path}: {e}")
            if progress_callback:
                progress_callback(0.0, f"Error: {e}")
            return False

    def _write_markdown(self, path: Path, text: str, page_num: int):
        content = f"# Page {page_num}\n\n{text}\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _write_combined_markdown(self, path: Path, text_list: List[str]):
        content = ""
        for i, text in enumerate(text_list, 1):
            content += f"# Page {i}\n\n{text}\n\n---\n\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

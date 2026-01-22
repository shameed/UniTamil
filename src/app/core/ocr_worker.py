"""
OCR Worker Module - Runs in a separate process for killable OCR.
"""
import pytesseract
from PIL import Image
import io
import sys
import base64

def run_ocr(image_bytes: bytes, lang: str = 'tam+eng') -> str:
    """
    Run OCR on image bytes. This function is designed to be called
    from a separate process.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except Exception as e:
        return f"[OCR_ERROR: {e}]"

def main():
    """
    Main entry point for the OCR worker process.
    Reads base64 image from stdin, prints result to stdout.
    """
    try:
        # Read all of stdin
        encoded_input = sys.stdin.read()
        if not encoded_input:
            return

        # Decode and run
        image_bytes = base64.b64decode(encoded_input)
        result = run_ocr(image_bytes)
        
        # Print result to stdout (utf-8)
        # Print result to stdout (utf-8)
        # Using sys.stdout.buffer.write to ensure encoding safety if needed
        # We MUST use buffer for unicode characters on Windows console
        sys.stdout.buffer.write(result.encode('utf-8'))
        sys.stdout.buffer.flush()
    except Exception as e:
        error_msg = f"[OCR_ERROR: {e}]"
        sys.stdout.buffer.write(error_msg.encode('utf-8'))
        sys.stdout.buffer.flush()

# Entry point for subprocess (if run directly)
if __name__ == "__main__":
    import base64
    main()

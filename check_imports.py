import sys
print(f"Python: {sys.executable}")
try:
    import fitz
    print("fitz imported")
    import pytesseract
    print("pytesseract imported")
    import flet
    print("flet imported")
    import PIL
    print("PIL imported")
    from app.core.pipeline import ProcessingPipeline
    print("ProcessingPipeline imported")
except Exception as e:
    print(f"ERROR: {e}")

# UniTamil - PDF to Markdown Converter

A Windows standalone utility to convert batch PDF files into clean Tamil Unicode Markdown output.

## Features

- **Legacy to Unicode**: Converts Bamini, TAB, and other legacy fonts to Unicode.
- **Hybrid Extraction**: Uses text extraction where possible, and Tesseract OCR for scanned pages.
- **Offline & Private**: Runs completely offline.
- **Format Preservation**: Keeps English text exactly as is, normalizes Tamil text.

## Prerequisites

1. **Windows 10/11**
2. **Tesseract OCR**: This application relies on Tesseract OCR being installed on your system.
   - Download: [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to default location: `C:\Program Files\Tesseract-OCR`
   - **Language Packs**: During installation, ensure you select **Tamil** and **English** scripts.

## Installation / Development

1. Clone the repository.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the application:
   ```powershell
   python src/main.py
   ```

## Building the EXE

To build the single executable file:

1. Ensure `pyinstaller` is installed.
2. Run:
   ```powershell
   pyinstaller unitamil.spec
   ```
3. The executable will be in `dist/Unitamil.exe`.

## Usage

1. Launch the application.
2. If Tesseract is missing, the app will guide you.
3. Select an **Input Folder** containing PDF files.
4. Select an **Output Folder** for the resulting Markdown.
5. Click **Start Processing**.

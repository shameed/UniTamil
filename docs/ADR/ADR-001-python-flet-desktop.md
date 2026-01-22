# ADR-001: Selection of Python & Flet for Desktop Utility

## Context

The workspace standard mandates .NET 10 (Back-end) and Angular (Front-end). However, the specific requirement for "Unitamil" is a **standalone, offline-capable, single-file executable (EXE)** desktop utility that runs on Windows machines without requiring a complex web server installation or .NET runtime prerequisites.

## Decision

We will deviate from the standard and use **Python 3.10** with **Flet** (Flutter wrapper) and **PyInstaller**.

## Justification

1.  **Single EXE Requirement**: Python + PyInstaller allows bundling the entire runtime and dependencies into a single portable `.exe` file. Achieving this with a .NET Core app often requires the user to install the .NET Runtime or results in a massive "Self-Contained" deployment that is less portable than a PyInstaller bundle.
2.  **Flet for UI**: Flet allows building modern, reactive UIs using Python backend logic directly, without a separate frontend build process (Node/Webpack). This simplifies the "Offline" architecture significantly—no local web server is needed; Flet handles the windowing natively.
3.  **Tesseract Integration**: Python has best-in-class libraries (`pytesseract`, `pymupdf`) for OCR and PDF manipulation, which are the core business logic.
4.  **Development Speed**: Python allows rapid iteration for file-system heavy operations (batch processing).

## Consequences

- **Deviation**: This project cannot share code with other .NET/Angular workspace projects.
- **Maintenance**: Requires Python expertise, though the workspace standard focuses on C#/Typescript.
- **Size**: The final EXE might be large (~30-50MB) due to bundled Python runtime, but this is acceptable for a desktop utility.

## Compliance

- **DoD**: We will still enforce strict linting (via `ruff`/`pylint` equivalent) and testing to meet the workspace's quality standards, adapting the spirit of the rules to Python.

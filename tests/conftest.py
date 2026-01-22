import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("src"))

@pytest.fixture
def sample_pdf_path(tmp_path):
    # Create a dummy PDF file for testing (empty)
    p = tmp_path / "test.pdf"
    p.write_bytes(b"%PDF-1.4...")
    return str(p)

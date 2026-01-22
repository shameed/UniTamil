from unittest.mock import patch, MagicMock
from app.core.dependency_checker import DependencyChecker

@patch("shutil.which")
def test_tesseract_found_in_path(mock_which):
    mock_which.return_value = "/usr/bin/tesseract"
    checker = DependencyChecker()
    assert checker.check_tesseract() is True
    assert checker.tesseract_path == "/usr/bin/tesseract"

@patch("shutil.which")
def test_tesseract_not_found(mock_which):
    mock_which.return_value = None
    # We also need to mock Path.exists to fail common paths
    with patch("pathlib.Path.exists", return_value=False):
        checker = DependencyChecker()
        assert checker.check_tesseract() is False

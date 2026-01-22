from unittest.mock import MagicMock, patch
from app.core.pipeline import ProcessingPipeline

path_str = "app.core.pipeline"

@patch(f"{path_str}.PDFExtractor")
@patch(f"{path_str}.LegacyConverter")
@patch(f"{path_str}.Normalizer")
def test_pipeline_process(MockNorm, MockConv, MockExt, tmp_path):
    # Setup mocks
    mock_extractor = MockExt.return_value
    mock_extractor.process_pdf.return_value = [
        {"page_num": 1, "text": "Page 1 Text", "method": "text"}
    ]
    
    mock_conv = MockConv.return_value
    mock_conv.convert.side_effect = lambda x: x # Identity
    
    mock_norm = MockNorm.return_value
    mock_norm.normalize.side_effect = lambda x: x # Identity
    
    pipeline = ProcessingPipeline()
    
    input_pdf = tmp_path / "input.pdf"
    input_pdf.touch()
    output_dir = tmp_path / "output"
    
    success = pipeline.process_file(str(input_pdf), str(output_dir))
    
    assert success is True
    assert (output_dir / "input" / "metadata.json").exists()

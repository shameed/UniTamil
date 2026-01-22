from app.core.normalizer import Normalizer
import unicodedata

def test_normalizer_nfc():
    norm = Normalizer()
    # Decomposed tamil 'ka' + 'i' -> 'ki'
    decomposed = "example" # Placeholder fixture
    # Ideally we use real tamil chars
    
    # Test 1: Simple ASCII pass-through
    assert norm.normalize("Hello") == "Hello"
    
    # Test 2: Verify NFC property
    # 'Amelie' with acute accent: \u00C9 vs \u0045\u0301
    composed = "\u00C9" 
    decomposed = "\u0045\u0301"
    assert norm.normalize(decomposed) == composed

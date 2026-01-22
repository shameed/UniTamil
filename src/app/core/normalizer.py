import unicodedata
from ..utils.logger import logger

class Normalizer:
    def normalize(self, text: str) -> str:
        """
        Normalizes Tamil text to NFC (Normalization Form C).
        This is standard for Tamil Unicode.
        """
        try:
            return unicodedata.normalize('NFC', text)
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return text

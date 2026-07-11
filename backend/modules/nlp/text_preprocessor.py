import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def detect_and_translate(text: str) -> Tuple[str, str]:
    """Detect language and translate to English if needed."""
    try:
        from deep_translator import GoogleTranslator
        from langdetect import detect

        lang = detect(text)
        if lang != "en":
            translated = GoogleTranslator(source=lang, target="en").translate(text)
            logger.info(f"Translated from {lang} to English")
            return translated, lang
    except ImportError:
        logger.warning("langdetect or deep-translator not installed")
    except Exception as e:
        logger.warning(f"Translation failed: {e}")

    return text, "en"


def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\.,!?-]", "", text)
    return text

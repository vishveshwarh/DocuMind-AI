# Handles language detection and preference
# Isolated so it can be swapped or extended easily

from langdetect import detect, LangDetectException
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

class LanguageService:
    def __init__(self):
        self.detected_language: str = "en"
        self.lang_preference: str = "en"   # "en" or "original"

    def detect_language(self, text: str) -> str:
        """Detect language from text sample. Returns language code e.g. 'hi', 'en'"""
        try:
            lang = detect(text)
            self.detected_language = lang
            logger.info(f"Detected language: {lang} ({self.get_language_name(lang)})")
            return lang
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}. Defaulting to English.")
            self.detected_language = "en"
            return "en"

    def set_preference(self, preference: str):
        """Set user's language preference: 'en' or 'original'"""
        self.lang_preference = preference
        logger.info(f"Language preference set to: {preference}")

    def get_language_name(self, lang_code: str) -> str:
        """Convert language code to display name"""
        return settings.LANGUAGE_NAMES.get(lang_code, lang_code.upper())

    def get_prompt_instruction(self) -> str:
        """Returns instruction string injected into LLM prompt"""
        if self.lang_preference == "en":
            return "Always respond in English regardless of the document language."
        else:
            lang_name = self.get_language_name(self.detected_language)
            return f"Always respond in {lang_name} language."

    def is_english(self) -> bool:
        return self.detected_language == "en"

# Single instance shared across the app
language_service = LanguageService()
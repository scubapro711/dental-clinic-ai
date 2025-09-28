 
import pytest
from src.shared.i18n_ready_solution import (
    get_message,
    detect_language,
    detect_language_advanced,
    get_supported_languages,
    add_translation,
    TRANSLATIONS
)
from unittest.mock import patch

class TestI18nSolution:
    def test_get_message(self):
        assert get_message("welcome", "en") == "Welcome to the dental clinic"
        assert get_message("welcome", "he") == "ברוכים הבאים למרפאת השיניים"
        assert get_message("welcome", "ar") == "مرحباً بكم في عيادة الأسنان"

    def test_get_message_with_params(self):
        assert get_message("patient_found", "en", name="John", age=30) == "Patient found: John, age 30"
        assert get_message("patient_found", "he", name="יוסי", age=40) == "נמצא מטופל: יוסי, גיל 40"

    def test_get_message_fallback(self):
        assert get_message("non_existent_key", "en") == "non_existent_key"
        assert get_message("welcome", "fr") == "ברוכים הבאים למרפאת השיניים" # Fallback to Hebrew

    def test_detect_language(self):
        assert detect_language("Hello") == "en"
        assert detect_language("שלום") == "he"
        assert detect_language("مرحبا") == "ar"
        assert detect_language("") == "he" # Default to Hebrew

    @patch("langdetect.detect")
    def test_detect_language_advanced(self, mock_detect):
        mock_detect.return_value = "en"
        assert detect_language_advanced("Hello") == "en"
        mock_detect.return_value = "he"
        assert detect_language_advanced("שלום") == "he"
        mock_detect.return_value = "ar"
        assert detect_language_advanced("مرحبا") == "ar"

    def test_get_supported_languages(self):
        supported = get_supported_languages()
        assert "he" in supported
        assert "en" in supported
        assert "ar" in supported

    def test_add_translation(self):
        add_translation("test_key", {"en": "Test", "he": "בדיקה", "ar": "اختبار"})
        assert get_message("test_key", "en") == "Test"
        assert get_message("test_key", "he") == "בדיקה"
        assert get_message("test_key", "ar") == "اختبار"


from googletrans import Translator
import logging
import time

# Local logger (avoid reconfiguring root logger)
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        # Using the public Google Translate endpoint is more reliable
        # for googletrans and reduces ConnectionTerminated errors
        self.translator = Translator(service_urls=[
            'translate.googleapis.com',
            'translate.google.com'
        ])
    
    def translate_text(self, text, target_language='en', source_language='auto'):
        """
        Translate text to target language
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (e.g., 'hi', 'es', 'fr')
            source_language (str): Source language code (default: 'auto' for auto-detection)
        
        Returns:
            dict: Translation result with original text, translated text, and language info
        """
        try:
            if not text or not text.strip():
                return {
                    'original_text': text,
                    'translated_text': text,
                    'source_language': source_language,
                    'target_language': target_language,
                    'success': True
                }

            # Retry to mitigate transient HTTP/2 connection terminations
            last_error = None
            for attempt in range(3):
                try:
                    result = self.translator.translate(
                        text,
                        dest=target_language,
                        src=source_language
                    )
                    return {
                        'original_text': text,
                        'translated_text': result.text,
                        'source_language': getattr(result, 'src', source_language),
                        'target_language': target_language,
                        'success': True
                    }
                except Exception as inner_e:
                    last_error = inner_e
                    # small backoff before retrying
                    time.sleep(0.2 * (attempt + 1))

            # If all retries failed, report gracefully
            raise last_error or Exception('Unknown translation error')

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                'original_text': text,
                'translated_text': text,  # Return original text if translation fails
                'source_language': source_language,
                'target_language': target_language,
                'success': False,
                'error': str(e)
            }
    
    def get_supported_languages(self):
        """
        Get list of supported languages
        
        Returns:
            dict: Dictionary of language codes and names
        """
        return {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'pa': 'Punjabi',
            'or': 'Odia',
            'as': 'Assamese',
            'ne': 'Nepali',
            'si': 'Sinhala',
            'my': 'Burmese',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'tl': 'Filipino'
        }

# Global instance
translation_service = TranslationService()

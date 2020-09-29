"""Wrapper on java.util.Locale to get android locale and language."""
try:
    on_android = True
    import android
    import jnius
except ImportError:
    on_android = False

# List of supported languages. If the found locale isn't one of these,
# fallback to en.
supported_languages = ['en', 'it']

current_locale = None
current_lang = 'en'
if on_android:
    _java_util_locale = jnius.autoclass('java.util.Locale')
    current_locale = _java_util_locale.getDefault()
    java_locale = str(current_locale.language)
    current_lang = (java_locale if java_locale in supported_languages
                    else current_lang)

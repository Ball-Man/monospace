"""Wrapper on java.util.Locale to get android locale and language."""
try:
    on_android = True
    import android
    import jnius
except ImportError:
    on_android = False

current_locale = None
current_lang = 'en'
if on_android:
    _java_util_locale = jnius.autoclass('java.util.Locale')
    current_locale = _java_util_locale.getDefault()
    current_lang = str(current_locale.language)

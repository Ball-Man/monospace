try:
    import android
    import jnius
except ImportError:
    pass


def toggle_keyboard():
    PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
    cur_activity = PythonActivity.mActivity
    Context = jnius.autoclass('android.content.Context')
    InputMethodManager = jnius.autoclass(
        'android.view.inputmethod.InputMethodManager')

    input_manager = cur_activity.getSystemService(Context.INPUT_METHOD_SERVICE)
    input_manager.toggleSoftInput(InputMethodManager.SHOW_FORCED, 0)

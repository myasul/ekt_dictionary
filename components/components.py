import re

from kivy.app import App
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty


class AutoDismissPopup(Popup):
    def __init__(self, **kwargs):
        super(AutoDismissPopup, self).__init__(**kwargs)
        Clock.schedule_once(self.dismiss, 1)


class DeletePopup(Popup):
    def __init__(self, screen, **kwargs):
        super(DeletePopup, self).__init__(**kwargs)
        self.screen = screen


class FilterPopup(Popup):
    def __init__(self, screen, **kwargs):
        super(FilterPopup, self).__init__(**kwargs)
        self.screen = screen


class FilterCheckBox(CheckBox):
    value = StringProperty()

    def __init__(self, **kwargs):
        super(FilterCheckBox, self).__init__(**kwargs)


class DictEntry(Label):
    kapampangan = StringProperty()
    tagalog = StringProperty()
    english = StringProperty()
    screen = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            # Retrieve Dictionary Screen
            screen_manager = App.get_running_app().root
            dict_screen = screen_manager.get_screen('dict_entry')

            # Set data to Dictionary Screen
            dict_screen.kapampangan = self.kapampangan
            dict_screen.english = self.english
            dict_screen.tagalog = self.tagalog
            dict_screen.back_screen = self.screen

            # Redirect to Dictionary Screen
            screen_manager.current = 'dict_entry'


class DictTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        dict_regex = re.compile(r"^[-'\sa-z]+$", re.I | re.M)
        if dict_regex.search(substring) and len(self.text) <= 49:
            return super(DictTextInput, self)\
                .insert_text(substring, from_undo=from_undo)

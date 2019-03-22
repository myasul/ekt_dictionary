#!/usr/bin/env python3

import re

# Imports from SQLite library
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import model.database_helper as db_helper

# Imports from Kivy library
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Rectangle, Color
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from kivy.logger import Logger
from borderbehaviour import BorderBehavior
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'fullscreen', 0)

# Kivy screens
from screens.add_screen import AddScreen
from screens.search_screen import SearchScreen
from screens.list_screen import ListScreen
from screens.dict_screen import DictScreen

import re

class DictTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        dict_regex = re.compile(r"^[-'\sa-z]+$", re.I | re.M)
        if dict_regex.search(substring) and len(self.text) <= 49:
            return super(DictTextInput, self)\
                .insert_text(substring, from_undo=from_undo)
                
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


class HomeScreen(Screen):
    pass


class EditScreen(Screen):
    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.kapampangan = StringProperty()
        self.tagalog = StringProperty()
        self.english = StringProperty()
        self.db_object = None

    def on_pre_enter(self):
        self.set_text_from_dict_val()

    def set_text_from_dict_val(self):
        self.ids.kapampangan_es.text = self.kapampangan
        self.ids.tagalog_es.text = self.tagalog
        self.ids.english_es.text = self.english

    def set_dict_val_from_text(self):
        self.kapampangan = self.ids.kapampangan_es.text
        self.tagalog = self.ids.tagalog_es.text
        self.english = self.ids.english_es.text

    def on_save(self):
        if self.db_object:
            try:
                self.set_dict_val_from_text()
                self.db_object.kapampangan = self.kapampangan
                self.db_object.tagalog = self.tagalog
                self.db_object.english = self.english
                db_helper.session.add(self.db_object)
                db_helper.session.commit()
                self.go_to_dict_screen()
            except SQLAlchemyError as e:
                # TODO :: Add logging
                print("Error: {}".format(e))
                db_helper.session.rollback()
                self.popup('Error Message', 'Error occured. Please report.')
        else:
            self.popup('Error Message', 'Error occured. Please report.')

    def go_to_dict_screen(self):
        self.update_dict_screen()
        self.manager.current = 'dict_entry'

    def update_dict_screen(self):
        screen_manager = App.get_running_app().root
        dict_entry = screen_manager.get_screen('dict_entry')
        dict_entry.kapampangan = self.kapampangan
        dict_entry.tagalog = self.tagalog
        dict_entry.english = self.english

    def get_entry(self):
        # Get dictionary data using the word selected
        # by the user from the List Screen
        entries, error = db_helper.search_entry(
            kapampangan=self.kapampangan,
            english=self.english,
            tagalog=self.tagalog)
        if error:
            # TODO :: Add logging
            return None
        return entries

    def popup(self, title, message):
        # Generic popup for error and confirmation messages
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title,
                                 content=content,
                                 size_hint=(0.4, 0.2))
        popup.open()


class EditInput(DictTextInput):
    pass


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


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.id = 'dict_sm'


ekt = Builder.load_file("ekt.kv")


class MainApp(App):
    title = 'EKT Dictionary'

    def build(self):
        return ekt


if __name__ == "__main__":
    MainApp().run()

#!/usr/bin/env python3

# Imports from SQLite library
import time
from sqlalchemy import create_engine, asc, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from database_setup import Dictionary, Base

# Imports from Kivy library
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Rectangle, Color
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '1500')
# Config.set('graphics', 'fullscreen', 0)


# Connect to the database and create a database session
engine = create_engine('sqlite:///ekt_dictionary.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=True)
session = DBSession()


class AddScreen(Screen):
    def clear_text_inputs(self):
        self.ids.e_input.text = ''
        self.ids.k_input.text = ''
        self.ids.t_input.text = ''

    def add_entry(self):
        # TODO :: Make the error message's box size dynamic
        try:
            if not self.are_fields_empty():
                new_dict_entry = Dictionary(tagalog=self.ids.t_input.text,
                                            kapampangan=self.ids.k_input.text,
                                            english=self.ids.e_input.text)
                session.add(new_dict_entry)
                session.commit()
                self.popup('Confirmation Message', 'Dictionary entry saved!')
                self.clear_text_inputs()
            else:
                self.popup('Error Message', 'Entry already exists!')
        except IntegrityError:
            self.popup('Error Message', 'Entry already exists!')
            session.rollback()
            self.clear_text_inputs()

    def popup(self, title, message):
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title,
                      content=content,
                      size_hint=(0.4, 0.2))
        popup.open()

    def are_fields_empty(self):
        if not all([self.ids.e_input.text,
                    self.ids.k_input.text,
                    self.ids.t_input.text]):
            return True
        return False


class SearchScreen(Screen):
    pass


class ListScreen(Screen):
    def on_pre_enter(self):
        all_entries = self.show_all_entries()
        row_num = len(all_entries)

        self.ids.list_grid.rows = row_num
        for entry in all_entries:
            self.ids.list_grid.add_widget(
                DictEntry(
                    text=entry.kapampangan,
                    font_size=25,
                )
            )

    def on_leave(self):
        delete_widgets = []
        for widget in self.ids.list_grid.children:
            if isinstance(widget, DictEntry):
                delete_widgets.append(widget)

        for widget in delete_widgets:
            self.ids.list_grid.remove_widget(widget)

    def show_all_entries(self):
        try:
            return session.query(Dictionary) \
                .order_by(Dictionary.kapampangan.asc()) \
                .all()
        except IntegrityError:
            # TODO :: Add logging
            self.popup('Error Message', 'Error Occured. Please report.')
            return None

    def popup(self, title, message):
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = Popup(title=title,
                      content=content,
                      size_hint=(0.4, 0.2))
        popup.open()


class DictEntry(Label):

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            screen_manager = App.get_running_app().root
            dict_screen = screen_manager.get_screen('dict_entry')
            dict_screen.current_kapampangan = self.text
            screen_manager.current = 'dict_entry'


class HomeScreen(Screen):
    pass


class DictScreen(Screen):
    def __init__(self, **kwargs):
        super(DictScreen, self).__init__(**kwargs)
        self.current_kapampangan = StringProperty()

    def on_pre_enter(self):
        # Populate the Labels with the data retrieved from database
        entry = self.get_entry()
        self.ids.kapampangan_ds.text = "Kapampangan: {}".format(
            entry.kapampangan)
        self.ids.tagalog_ds.text = "Tagalog: {}".format(entry.tagalog)
        self.ids.english_ds.text = "English: {}".format(entry.english)

    def show_delete_popup(self):
        delete_popup = DeletePopup(self)
        delete_popup.open()

    def on_confirm_delete(self, popup):
        popup.dismiss()
        self.delete_entry()

    def delete_entry(self):
        # Deletes this specific dictionary entry.
        # User will also be redirected to the List screen.
        if self.current_kapampangan:
            entry = self.get_entry()
            session.delete(entry)
            try:
                session.commit()
                # Multiple delays are in place to display
                # all information needed simultaneously
                self.popup('Confirmation Message',
                           'Dictionary entry deleted!')
                Clock.schedule_once(self.go_to_list_screen, 1.5)
            except SQLAlchemyError as e:
                # TODO :: Add logging
                print("Error: {}".format(e))
                self.popup('Error Message', 'Error occured. Please report.')
        else:
            # TODO :: Add logging
            self.popup('Error Message', 'Error occured. Please report.')

    def go_to_list_screen(self, *args):
        self.manager.current = 'list'

    def get_entry(self):
        # Get dictionary data using the word selected
        # by the user from the List Screen
        if self.current_kapampangan:
            return session.query(Dictionary) \
                .filter(Dictionary.kapampangan == self.current_kapampangan) \
                .one()
        else:
            # TODO :: Add logging
            self.popup('Error Message', 'Error occured. Please report.')
            return None

    def popup(self, title, message):
        # Generic popup for error and confirmation messages
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title,
                      content=content,
                      size_hint=(0.4, 0.2))
        popup.open()

class AutoDismissPopup(Popup):
    def __init__(self, **kwargs):
        super(AutoDismissPopup, self).__init__(**kwargs)
        Clock.schedule_once(self.dismiss, 1)

class DeletePopup(Popup):
    def __init__(self, screen, **kwargs):
        super(DeletePopup, self).__init__(**kwargs)
        self.screen = screen

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

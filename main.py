#!/usr/bin/env python3

# Imports from SQLite library
import re
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
from borderbehaviour import BorderBehavior
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '1500')
# Config.set('graphics', 'fullscreen', 0)


# Connect to the database and create a database session
engine = create_engine('sqlite:///ekt_dictionary.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=True)
session = DBSession()


class DictTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        dict_regex = re.compile(r"^[-'\sa-z]+$", re.I | re.M)
        if dict_regex.search(substring) and len(self.text) <= 49:
            return super(DictTextInput, self).insert_text(substring, from_undo=from_undo)


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


class DictInput(DictTextInput):
    pass

class SearchScreen(Screen):
    pass
    
class ListScreen(Screen):
    def on_pre_enter(self):
        all_entries = self.show_all_entries()
        self.add_entry_widgets(all_entries)

    def on_leave(self):
        self.clear_entries()

    def clear_entries(self):
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

    def do_search(self, search_str):
        # TODO :: Make it dynamic so the user can search in all languages
        self.clear_entries()
        entries = self.search_text_kapampangan(search_str)
        print(entries)
        if len(entries) > 0:
            self.add_entry_widgets(entries)

    def search_text_kapampangan(self, search_str):
        try:
            print("Search String: {}".format(search_str))
            return session.query(Dictionary) \
                .filter(Dictionary.kapampangan.like("{}%".format(search_str))) \
                .order_by(Dictionary.kapampangan.asc()) \
                .all()
        except IntegrityError:
            # TODO :: Add logging
            self.popup('Error Message', 'Error Occured. Please report.')
            return None

    def add_entry_widgets(self, entries):
        row_num = len(entries)

        self.ids.list_grid.rows = row_num
        for entry in entries:
            self.ids.list_grid.add_widget(
                DictEntry(
                    text=entry.kapampangan,
                    font_size=25,
                )
            )

    def popup(self, title, message):
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = Popup(title=title,
                      content=content,
                      size_hint=(0.4, 0.2))
        popup.open()


class SearchTextInput(DictTextInput):
    def __init__(self, **kwargs):
        super(SearchTextInput, self).__init__(**kwargs)

    def keyboard_on_key_up(self, window, keycode):
        print("Search Text: {}".format(self.text))
        self.search_matched_entries()
        return super(SearchTextInput, self).keyboard_on_key_up(window, keycode)

    def search_matched_entries(self):
        screen_manager = App.get_running_app().root
        list_screen = screen_manager.get_screen('list')
        list_screen.do_search(self.text)


class DictEntry(Label):

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            screen_manager = App.get_running_app().root
            dict_screen = screen_manager.get_screen('dict_entry')
            dict_screen.kapampangan = self.text
            screen_manager.current = 'dict_entry'


class HomeScreen(Screen):
    pass


class DictScreen(Screen):
    def __init__(self, **kwargs):
        super(DictScreen, self).__init__(**kwargs)
        self.kapampangan = StringProperty()
        self.tagalog = StringProperty()
        self.english = StringProperty()

    def set_dict_entry(self, entry):
        self.kapampangan = entry.kapampangan
        self.tagalog = entry.tagalog
        self.english = entry.english

    def on_pre_enter(self):
        # Populate the Labels with the data retrieved from database
        print("Entering Dictionary Screen")
        entry = self.get_entry()
        self.set_dict_entry(entry)
        self.ids.kapampangan_ds.text = self.kapampangan
        self.ids.tagalog_ds.text = self.tagalog
        self.ids.english_ds.text = self.english

    def show_delete_popup(self):
        delete_popup = DeletePopup(self)
        delete_popup.open()

    def on_confirm_delete(self, popup):
        popup.dismiss()
        self.delete_entry()

    def delete_entry(self):
        # Deletes this specific dictionary entry.
        # User will also be redirected to the List screen.
        if self.kapampangan:
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

    def on_edit_entry(self):
        screen_manager = App.get_running_app().root
        edit_entry = screen_manager.get_screen('edit_entry')
        edit_entry.kapampangan = self.kapampangan
        edit_entry.tagalog = self.tagalog
        edit_entry.english = self.english
        screen_manager.current = 'edit_entry'

    def go_to_list_screen(self, *args):
        self.manager.current = 'list'

    def get_entry(self):
        # Get dictionary data using the word selected
        # by the user from the List Screen
        if self.kapampangan:
            return session.query(Dictionary) \
                .filter(Dictionary.kapampangan == self.kapampangan) \
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


class EditScreen(Screen):
    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.kapampangan = StringProperty()
        self.tagalog = StringProperty()
        self.english = StringProperty()

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
        try:
            entry = self.get_entry()
            self.set_dict_val_from_text()
            entry.kapampangan = self.kapampangan
            entry.tagalog = self.tagalog
            entry.english = self.english
            session.add(entry)
            session.commit()
            self.go_to_dict_screen()
        except SQLAlchemyError as e:
            # TODO :: Add logging
            print("Error: {}".format(e))
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
        if self.kapampangan:
            return session.query(Dictionary) \
                .filter(Dictionary.kapampangan == self.kapampangan) \
                .one()

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

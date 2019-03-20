#!/usr/bin/env python3

import re

# Imports from SQLite library
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import database_helper as db_helper

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
from borderbehaviour import BorderBehavior
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'fullscreen', 0)

import re

class DictTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        dict_regex = re.compile(r"^[-'\sa-z]+$", re.I | re.M)
        if dict_regex.search(substring) and len(self.text) <= 49:
            return super(DictTextInput, self)\
                .insert_text(substring, from_undo=from_undo)


class AddScreen(Screen):
    def clear_text_inputs(self):
        self.ids.e_input.text = ''
        self.ids.k_input.text = ''
        self.ids.t_input.text = ''

    def add_entry(self):
        # TODO :: Make the error message's box size dynamic
        if self.has_no_empty_fields():
            try:
                new_dict_entry = db_helper.Dictionary(
                    tagalog=self.ids.t_input.text,
                    kapampangan=self.ids.k_input.text.lower(),
                    english=self.ids.e_input.text)
                db_helper.session.add(new_dict_entry)
                db_helper.session.commit()
                self.popup('Confirmation Message', 'Dictionary entry saved!')
                self.clear_text_inputs()
            except IntegrityError:
                self.popup('Error Message', 'Entry already exists!')
                db_helper.session.rollback()
                self.clear_text_inputs()
        else:
            self.popup('Error Message', 'All the fields are mandatory!')

    def popup(self, title, message):
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title,
                                 content=content,
                                 size_hint=(0.4, 0.2))
        popup.open()

    def has_no_empty_fields(self):
        if all([self.ids.e_input.text,
                self.ids.k_input.text,
                self.ids.t_input.text]):
            return True
        return False

class DictInput(DictTextInput):
    pass

class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super(SearchScreen, self).__init__(**kwargs)
        self.search_mode = 1
        self.language = 'kapampangan'
        self.filter_popup = FilterPopup(self)
        self.search_codes = {
                            "exact_match": 0,
                            "starts with": 1,
                            "contains": 2,
                            }

    def show_filter_popup(self):
        self.filter_popup.open()

    def set_language(self, language):
        self.language = language

    def set_search_mode(self, match):
        self.search_mode = self.search_codes.get(match)

    def get_search_text(self):
        return self.ids.search_input.text        

    def on_search(self):
        results, error = self.do_search()
        if error:
            # TODO :: Add logging
            self.popup('Error Message', 'Error Occured. Please report.')
            return

        if results is None:
            self.popup('Message', 'No results found!')
        else:
            self.display_results(results)

    def do_search(self):
        self.clear_results()
        if self.search_mode:
            search_text = self.get_search_text()
            if self.language == 'kapampangan':
                return db_helper.search_in_kapampangan(search_text, self.search_mode)
            elif self.language == 'english':
                return db_helper.search_in_english(search_text, self.search_mode)
            elif self.language == 'tagalog':
                return db_helper.search_in_tagalog(search_text, self.search_mode)
            else:
                # TODO :: Add logging
                self.popup('Error message',
                        'Invalid language. Please report.')
        else:
            # TODO :: Add logging
            self.popup('Error message',
                    'Invalid language. Please report.')

    def clear_results(self):
        delete_widgets = []
        for widget in self.ids.list_grid.children:
            if isinstance(widget, DictEntry):
                delete_widgets.append(widget)

        for widget in delete_widgets:
            self.ids.list_grid.remove_widget(widget)

    def display_results(self, entries):
        row_num = len(entries)
        self.ids.list_grid.rows = row_num
        for entry in entries:
            # print(db_helper.object_as_dict(entry))
            dict_entry = DictEntry(
                text=entry.kapampangan,
                font_size=25,
                halign='left',
                valign='middle',
                screen='search',
                kapampangan=entry.kapampangan,
                tagalog=entry.tagalog,
                english=entry.english
            )
            dict_entry.bind(size=dict_entry.setter('text_size'))
            self.ids.list_grid.add_widget(dict_entry)

    def popup(self, title, message):
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = Popup(title=title,
                      content=content,
                      size_hint=(0.4, 0.2))
        popup.open()

class FilterToggleBtn(ToggleButton):
    def __init__(self, **kwargs):
        super(FilterToggleBtn, self).__init__(**kwargs)
        self.value = StringProperty(False)

class ListScreen(Screen):
    def on_pre_enter(self):
        all_entries = self.show_all_entries()
        if all_entries:
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
        entries, error = db_helper.get_all_entries()
        if error:
            # TODO :: Add logging
            self.popup('Error Message', 'Error Occured. Please report.')
            return
        return entries

    def do_search(self, search_str):
        # TODO :: Make it dynamic so the user can search in all languages
        self.clear_entries()
        entries = self.search_text_kapampangan(search_str)
        if len(entries) > 0:
            self.add_entry_widgets(entries)

    def search_text_kapampangan(self, search_str):
        entries, error = db_helper.search_in_kapampangan(search_str, 1)
        if error:
            # TODO :: Add logging
            self.popup('Error Message', 'Error Occured. Please report.')
            return
        return entries

    def add_entry_widgets(self, entries):
        row_num = len(entries)

        self.ids.list_grid.rows = row_num
        for entry in entries:
            dict_entry = DictEntry(
                text=entry.kapampangan,
                font_size=25,
                halign='left',
                valign='middle',
                screen='list',
                kapampangan=entry.kapampangan,
                tagalog=entry.tagalog,
                english=entry.english
            )
            dict_entry.bind(size=dict_entry.setter('text_size'))
            self.ids.list_grid.add_widget(dict_entry)

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
        self.search_matched_entries()
        return super(SearchTextInput, self).keyboard_on_key_up(window, keycode)

    def search_matched_entries(self):
        screen_manager = App.get_running_app().root
        list_screen = screen_manager.get_screen('list')
        list_screen.do_search(self.text)


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


class DictScreen(Screen):
    def __init__(self, **kwargs):
        super(DictScreen, self).__init__(**kwargs)
        self.kapampangan = StringProperty()
        self.tagalog = StringProperty()
        self.english = StringProperty()
        self.back_screen = StringProperty()
        self.db_object = None

    def set_dict_entry(self, entry):
        self.db_object = entry
        self.kapampangan = entry.kapampangan
        self.tagalog = entry.tagalog
        self.english = entry.english

    def on_pre_enter(self):
        # Populate the Labels with the data retrieved from database
        if self.kapampangan:
            print("ENTERED DICT SCREEN!")
            entry = self.get_entry()

            if not entry:
                self.popup('Error Message', 'Error occured. Please report.')
                return

            self.set_dict_entry(entry)
            self.ids.kapampangan_ds.text = self.kapampangan
            self.ids.tagalog_ds.text = self.tagalog
            self.ids.english_ds.text = self.english
        else:
            # TODO :: Add logging
            self.popup('Error Message', 'Error occured. Please report.')

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
            db_helper.session.delete(entry)
            try:
                db_helper.session.commit()
                # Multiple delays are in place to display
                # all information needed simultaneously
                self.popup('Confirmation Message',
                           'Dictionary entry deleted!')
                Clock.schedule_once(self.on_back, 1.5)
            except SQLAlchemyError as e:
                # TODO :: Add logging
                print("Error: {}".format(e))
                db_helper.session.rollback()
                self.popup('Error Message', 'Error occured. Please report.')
        else:
            # TODO :: Add logging
            self.popup('Error Message', 'Error occured. Please report.')

    def on_edit_entry(self):
        # Retrieve Edit Screen
        screen_manager = App.get_running_app().root
        edit_entry = screen_manager.get_screen('edit_entry')

        # Populate Edit Screen's class variables
        edit_entry.kapampangan = self.kapampangan
        edit_entry.tagalog = self.tagalog
        edit_entry.english = self.english
        edit_entry.db_object = self.db_object

        # Redirect to Edit Screen
        screen_manager.current = 'edit_entry'

    def on_back(self):
        self.manager.current = self.back_screen

    def go_to_list_screen(self, *args):
        self.manager.current = 'list'

    def get_entry(self):
        # Get dictionary data using the word selected
        # by the user from the List Screen
        entry, error = db_helper.search_entry(
            kapampangan=self.kapampangan,
            english=self.english,
            tagalog=self.tagalog)
        if error:
            # TODO :: Add logging
            return None
        return entry

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

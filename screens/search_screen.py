from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.logger import Logger

import os
from components.components import DictEntry, AutoDismissPopup
import model.database_helper as db_helper

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/search_screen.kv")

SEARCH_MODES = [
    "exact_match",
    "starts with",
    "contains",
]


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

    def on_pre_enter(self):
        # Clear the input text upon entering the Search screen.
        # Initial search with blank filters.
        self.ids.search_input.text = ""
        self.on_search()
        Logger.info("Application: Entering Search Screen.")

    def on_pre_leave(self):
        Logger.info("Application: Leaving Search Screen.")

    def show_filter_popup(self):
        self.filter_popup.open()

    def set_language(self, language):
        self.language = language

    def set_search_mode(self, match):
        self.search_mode = self.search_codes.get(match)

    def get_search_text(self):
        return self.ids.search_input.text

    def on_search(self):
        Logger.info("Application: Search start.")
        results, error = self.do_search()
        if error:
            Logger.error('Application: Error Stack: {}'.format(error))
            self.popup('Error Message', 'Error Occured. Please report.')
            return

        if results is None:
            self.popup('Message', 'No results found!')
        else:
            self.display_results(results)
        Logger.info("Application: Search complete.")

    def do_search(self):
        # Search the ekt database with the filters
        # set by the user.
        self.clear_results()
        Logger.info('Application: Searching using the following filters ' +
                    '(Language: {}, Search Mode: {})'.format(
                        self.language, SEARCH_MODES[self.search_mode]))
        if self.search_mode:
            search_text = self.get_search_text()
            if self.language == 'kapampangan':
                return db_helper.search_in_kapampangan(search_text,
                                                       self.search_mode)
            elif self.language == 'english':
                return db_helper.search_in_english(search_text,
                                                   self.search_mode)
            elif self.language == 'tagalog':
                return db_helper.search_in_tagalog(search_text,
                                                   self.search_mode)
            else:
                Logger.error(
                    'Application: Language {} is invalid.'.format(
                        self.language))
                self.popup('Error message',
                           'Invalid language. Please report.')
        else:
            Logger.error(
                'Application: Search mode {} is invalid.'.format(
                    self.search_mode))
            self.popup('Error message',
                       'Invalid Search mode. Please report.')

    def clear_results(self):
        # Method will remove old results.
        Logger.info('Application: Removing old results.')
        delete_widgets = []
        for widget in self.ids.list_grid.children:
            if isinstance(widget, DictEntry):
                delete_widgets.append(widget)

        for widget in delete_widgets:
            Logger.debug('Application: Removing {}'.format(widget.text))
            self.ids.list_grid.remove_widget(widget)

    def display_results(self, entries):
        # Depending on the results from the database,
        # this method will add Dictionary widgets on
        # the screen.
        Logger.info('Application: Displaying search results.')
        row_num = len(entries)
        self.ids.list_grid.rows = row_num
        for entry in entries:
            Logger.debug('Application: Adding {}.'.format(entry.kapampangan))
            dict_entry = DictEntry(
                text=entry.kapampangan,
                font_size=40,
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
        # Generic popup for error and confirmation messages
        content = Label(text=message,
                        font_size=40,
                        color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title,
                                 content=content,
                                 size_hint=(0.6, 0.3))
        popup.open()


class FilterPopup(Popup):
    def __init__(self, screen, **kwargs):
        super(FilterPopup, self).__init__(**kwargs)
        self.screen = screen


class FilterCheckBox(CheckBox):
    value = StringProperty()

    def __init__(self, **kwargs):
        super(FilterCheckBox, self).__init__(**kwargs)

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty
from kivy.lang import Builder

import os
from components.components import DictEntry
import model.database_helper as db_helper

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/search_screen.kv")


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
        self.ids.search_input.text = ""
        self.on_search()

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
                return db_helper.search_in_kapampangan(search_text,
                                                       self.search_mode)
            elif self.language == 'english':
                return db_helper.search_in_english(search_text,
                                                   self.search_mode)
            elif self.language == 'tagalog':
                return db_helper.search_in_tagalog(search_text,
                                                   self.search_mode)
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


class FilterPopup(Popup):
    def __init__(self, screen, **kwargs):
        super(FilterPopup, self).__init__(**kwargs)
        self.screen = screen


class FilterCheckBox(CheckBox):
    value = StringProperty()

    def __init__(self, **kwargs):
        super(FilterCheckBox, self).__init__(**kwargs)

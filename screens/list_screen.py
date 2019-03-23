from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder
import os

from components.components import DictTextInput, DictEntry
import model.database_helper as db_helper

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/list_screen.kv")


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

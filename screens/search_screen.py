from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.logger import Logger
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import os

# Internal imports
from components.borderbehaviour import BorderBehavior
from components.components import DictEntry, AutoDismissPopup
from components.scroll_border import ScrollBorder
from tools.const import MAX_ENTRIES, ROW_DEFAULT_HEIGHT, VALID_LANGUAGES
from tools import helper
import model.database_helper as db_helper

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/search_screen.kv")

SEARCH_MODES = ["exact_match", "starts with", "contains"]

# TODO: Add feature to go back to the "current state" when you are coming from
# Dict screen going back to the Search screen


class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super(SearchScreen, self).__init__(**kwargs)
        self.search_mode = 1
        self.language = "kapampangan"
        self.filter_popup = FilterPopup(self)
        self.search_codes = {"exact_match": 0, "starts with": 1, "contains": 2}

    def on_pre_enter(self):
        # Clear the input text upon entering the Search screen.
        # Initial search with blank filters.
        self.ids.search_input.text = ""
        self.on_click_search()
        Logger.info("Application: Entering Search Screen.")

    def on_pre_leave(self):
        Logger.info("Application: Leaving Search Screen.")

    def show_filter_popup(self):
        self.filter_popup.open()

    def set_language(self, language):
        # TODO :: Test every langu
        if language in VALID_LANGUAGES:
            self.language = language
        else:
            Logger.error(f"Application: Language {self.language} is invalid.")
            self.popup("Error message", "Invalid language. Please report.")

    def set_search_mode(self, mode):
        match = self.search_codes.get(mode)
        if isinstance(match, int):
            self.search_mode = match
        else:
            Logger.error(f"Application: Search mode {mode} is invalid.")
            self.popup("Error message", "Invalid search mode. Please report.")

    def get_search_text(self):
        return self.ids.search_input.text

    def on_click_search(self):
        Logger.info("Application: Search start.")
        self.clear_results()

        # Set the cursor at the top of the scroll view.
        self.ids.list_scroll.scroll_y = 1

        self.do_search()

    def do_search(self, next_row=MAX_ENTRIES, scroll=False):
        results, error = self.database_search(next_row, scroll)

        if error: 
            Logger.error("Application: Error Stack: {}".format(error))
            self.popup("Error Message", "Error Occured. Please report.")
            return

        result_count = len(results)
        if results and result_count > 0:
            row_count = next_row + result_count if scroll else result_count
            self.display_results(results, row_count)
        else:
            self.popup("Message", "No results found!")

        Logger.info("Application: Search complete.")

    def database_search(self, next_row, scroll):
        # Search the ekt database with the filters
        # set by the user.
        Logger.info(
            "Application: Searching using the following filters "
            + "(Language: {}, Search Mode: {})".format(
                self.language, SEARCH_MODES[self.search_mode]
            )
        )

        if not scroll:
            _, error = db_helper.clean_query_result()

            if not error:
                count, error = db_helper.dictionary_count(
                    self.get_search_text(), self.search_mode, self.language
                )

                if isinstance(count, int) and count > MAX_ENTRIES:
                    _, error = db_helper.add_query_result(5, next_row, count)

                if not error:
                    entries, error = db_helper.dictionary_search(
                        self.get_search_text(), self.search_mode, self.language
                    )
        else:
            entries, error = db_helper.dictionary_search(
                self.get_search_text(), self.search_mode, self.language, offset=next_row
            )

            if entries:
                _, error = db_helper.update_query_result(next_row + len(entries))

        if error:
            return None, error

        return entries, None

    def clear_results(self):
        # Method will remove old results.
        Logger.info("Application: Removing old results.")
        delete_widgets = []
        for widget in self.ids.list_grid.children:
            if isinstance(widget, DictEntry):
                delete_widgets.append(widget)

        for widget in delete_widgets:
            Logger.debug("Application: Removing {}".format(widget.text))
            self.ids.list_grid.remove_widget(widget)

    def display_results(self, entries, row_count):
        # Depending on the results from the database,
        # this method will add Dictionary widgets on
        # the screen.
        Logger.info("Application: Displaying search results.")

        Logger.info(f"Application: ADDING {row_count} ROWS")

        self.ids.list_grid.rows = row_count
        for entry in entries:
            Logger.debug("Application: Adding {}.".format(entry.kapampangan))
            dict_entry = DictEntry(
                text=entry.kapampangan,
                font_size=40,
                halign="left",
                valign="middle",
                screen="search",
                kapampangan=entry.kapampangan,
                tagalog=entry.tagalog,
                english=entry.english,
            )
            dict_entry.bind(size=dict_entry.setter("text_size"))
            self.ids.list_grid.add_widget(dict_entry)

    def popup(self, title, message):
        # Generic popup for error and confirmation messages
        content = Label(text=message, font_size=40, color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title, content=content, size_hint=(0.6, 0.3))
        popup.open()


class FilterPopup(Popup):
    def __init__(self, screen, **kwargs):
        super(FilterPopup, self).__init__(**kwargs)
        self.screen = screen


class FilterCheckBox(CheckBox):
    value = StringProperty()

    def __init__(self, **kwargs):
        super(FilterCheckBox, self).__init__(**kwargs)


class SearchScroll(ScrollBorder):
    def __init__(self, **kwargs):
        super(SearchScroll, self).__init__("search", **kwargs)

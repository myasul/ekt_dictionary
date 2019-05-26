from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.logger import Logger
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import os

# Internal imports
from components.borderbehaviour import BorderBehavior
from components.components import DictTextInput, DictEntry
from tools.const import MAX_ENTRIES, ROW_DEFAULT_HEIGHT
import model.database_helper as db_helper

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/list_screen.kv")

# TODO #1 :: Add meaningful comments
# TODO #2 :: Add meaningful logging statements


class ListScreen(Screen):
    def on_pre_enter(self):
        # Show all entries upon entering the list
        # screen for the first time.
        Logger.info("Application: Entering List screen.")
        self.do_search("")

    def on_leave(self):
        # Remove all widgets before leaving the List screen.
        # This would ensure that the list that the users
        # see is always up-to-date.
        Logger.info("Application: Leaving List screen.")
        # Clear text field
        self.ids.search_text.text = ""
        self.clear_entries()

    def clear_entries(self):
        # Method will remove old widgets before
        # adding the new search results.
        Logger.info("Application: Removing old entries.")
        delete_widgets = []
        for widget in self.ids.list_grid.children:
            if isinstance(widget, DictEntry):
                delete_widgets.append(widget)

        for widget in delete_widgets:
            Logger.debug("Application: Removing {}".format(widget.text))
            self.ids.list_grid.remove_widget(widget)

    def do_search(self, search_str=None, next_row=MAX_ENTRIES, scroll=False):
        Logger.info("Application: Search start.")

        if not scroll:
            self.clear_entries()

        entries = self.search_text_kapampangan(search_str, next_row, scroll)
        entries_count = len(entries)

        if entries and entries_count > 0:
            row_count = next_row + entries_count if scroll else entries_count
            self.add_entry_widgets(entries, row_count)
        Logger.info("Application: Search complete.")

    def search_text_kapampangan(self, search_str, next_row, scroll):
        # TODO :: Add meaningful comment
        # TODO :: Add meaningful logging statements

        if not scroll:
            _, error = db_helper.clean_query_result()

            if not error:
                count, error = db_helper.dictionary_count(search_str, 1, "kapampangan")

                if isinstance(count, int) and count > MAX_ENTRIES:
                    _, error = db_helper.add_query_result(6, next_row, count)

                if not error:
                    entries, error = db_helper.dictionary_search(
                        search_str, 1, "kapampangan"
                    )

        else:
            entries, error = db_helper.dictionary_search(
                search_str, 1, "kapampangan", offset=next_row
            )
            if entries:
                _, error = db_helper.update_query_result(next_row + len(entries))

        if error:
            Logger.error(f"Application: Error Stack: {error}")
            self.popup("Error Message", "Error Occured. Please report.")
            return

        return entries

    def add_entry_widgets(self, entries, row_count):
        # Depending on the results from the database,
        # this method will add Dictionary widgets on
        # the screen.
        Logger.info("Application: Displaying search results.")

        self.ids.list_grid.rows = row_count
        for entry in entries:
            Logger.debug("Application: Adding {}".format(entry.kapampangan))
            dict_entry = DictEntry(
                text=entry.kapampangan,
                font_size=40,
                halign="left",
                valign="middle",
                screen="list",
                kapampangan=entry.kapampangan,
                tagalog=entry.tagalog,
                english=entry.english,
            )
            dict_entry.bind(size=dict_entry.setter("text_size"))
            self.ids.list_grid.add_widget(dict_entry)

    def popup(self, title, message):
        # Generic popup for error and confirmation messages
        content = Label(text=message, font_size=20, color=[1, 1, 1, 1])
        popup = Popup(title=title, content=content, size_hint=(0.4, 0.2))
        popup.open()


class SearchTextInput(DictTextInput):
    def __init__(self, **kwargs):
        super(SearchTextInput, self).__init__(**kwargs)

    def keyboard_on_key_up(self, window, keycode):
        # Typing on search text input would
        # trigger the search function that would
        # enable the list screen to add results widgets
        # to its screen.
        self.search_matched_entries()
        return super(SearchTextInput, self).keyboard_on_key_up(window, keycode)

    def search_matched_entries(self):
        # Retrieve List Screen object
        screen_manager = App.get_running_app().root
        list_screen = screen_manager.get_screen("list")

        # Set the cursor at the top of the scroll view.
        list_screen.ids.list_scroll.scroll_y = 1

        list_screen.do_search(search_str=self.text)


class ListScroll(ScrollView, BorderBehavior):
    def on_touch_up(self, touch):
        # TODO :: Add meaningful comments
        if self.scroll_y <= 0:
            self.populate_with_additional_entries()
        return super().on_touch_up(touch)

    def populate_with_additional_entries(self):
        # TODO :: Add meaningful comments
        screen_manager = App.get_running_app().root
        list_screen = screen_manager.get_screen("list")

        qr, error = db_helper.get_query_result()
        if isinstance(error, NoResultFound):
            return
        elif isinstance(error, MultipleResultsFound):
            db_helper.clean_query_result()
            return
        elif error:
            Logger.error(f"Application: Error Stack: {error}")
            list_screen.popup("Error Message", "Error Occured. Please report.")

        if qr.next_row < qr.total_rows:
            list_screen.do_search(
                search_str=list_screen.ids.search_text.text,
                next_row=qr.next_row,
                scroll=True,
            )

            self.scroll_y += self.recalculate_scroll_y(qr.next_row)

    def recalculate_scroll_y(self, next_row):
        y = (MAX_ENTRIES * ROW_DEFAULT_HEIGHT) / (ROW_DEFAULT_HEIGHT * next_row)
        return float(y)

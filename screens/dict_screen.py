from sqlalchemy.exc import SQLAlchemyError
import os

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.logger import Logger

from components.components import DeletePopup, AutoDismissPopup
import model.database_helper as db_helper

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/dict_screen.kv")


class DictScreen(Screen):
    def __init__(self, **kwargs):
        self.kapampangan = StringProperty()
        self.tagalog = StringProperty()
        self.english = StringProperty()
        self.back_screen = StringProperty()
        self.db_object = None
        super(DictScreen, self).__init__(**kwargs)

    def set_dict_entry(self, entry):
        self.db_object = entry
        self.kapampangan = entry.kapampangan
        self.tagalog = entry.tagalog
        self.english = entry.english

    def on_pre_enter(self):
        Logger.info("Application: Entering Dictionary screen.")
        Logger.info(
            "Application: Viewing: K: {} - E: {} - T: {}".format(
                self.kapampangan, self.english, self.tagalog
            )
        )

        if self.kapampangan:
            entry = self.get_entry()

            if not entry:
                Logger.error("Application: Dictionary entry cannot found.")
                self.popup("Error Message", "Error occured. Please report.")
                return

            # Populate the Labels with the data retrieved from database
            self.set_dict_entry(entry)
            self.ids.kapampangan_ds.text = self.kapampangan
            self.ids.tagalog_ds.text = self.tagalog
            self.ids.english_ds.text = self.english
        else:
            Logger.error("Application: Dictionary entry cannot found.")
            self.popup("Error Message", "Error occured. Please report.")

    def on_pre_leave(self):
        Logger.info("Application: Leaving Dictionary Screen")

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
            try:
                db_helper.delete_dictionary(entry)
                self.popup("Confirmation Message", "Dictionary entry deleted!")
                # Multiple delays are in place to display
                # all information needed simultaneously
                Clock.schedule_once(self.on_back, 1.5)
            except SQLAlchemyError as e:
                db_helper.session.rollback()
                Logger.error("Application: Error Stack: {}".format(e))
                self.popup("Error Message", "Error occured. Please report.")
        else:
            Logger.error("Application: Dictionary entry cannot found.")
            self.popup("Error Message", "Error occured. Please report.")

    def on_edit_entry(self):
        # Retrieve Edit Screen
        screen_manager = App.get_running_app().root
        edit_entry = screen_manager.get_screen("edit_entry")

        # Populate Edit Screen's class variables
        edit_entry.kapampangan = self.kapampangan
        edit_entry.tagalog = self.tagalog
        edit_entry.english = self.english
        edit_entry.db_object = self.db_object

        # Redirect to Edit Screen
        screen_manager.current = "edit_entry"

    def on_back(self, *args):
        self.manager.current = self.back_screen

    def go_to_list_screen(self, *args):
        self.manager.current = "list"

    def get_entry(self):
        # Get dictionary data using the word selected
        # by the user from the List Screen
        entry, error = db_helper.search_entry(
            kapampangan=self.kapampangan, english=self.english, tagalog=self.tagalog
        )
        if error:
            Logger.error("Application: Error Stack: {}".format(error))
            return None
        return entry

    def popup(self, title, message):
        # Generic popup for error and confirmation messages
        content = Label(text=message, font_size=40, color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title, content=content, size_hint=(0.6, 0.3))
        popup.open()

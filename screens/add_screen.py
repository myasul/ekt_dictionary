from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.logger import Logger
import os
from sqlalchemy.exc import IntegrityError
from model import database_helper as db_helper
from components.components import AutoDismissPopup, DictTextInput

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/add_screen.kv")


class AddScreen(Screen):
    def clear_text_inputs(self):
        self.ids.e_input.text = ""
        self.ids.k_input.text = ""
        self.ids.t_input.text = ""

    def on_pre_enter(self):
        Logger.info("Application: Entering Add Screen")

    def on_pre_leave(self):
        Logger.info("Application: Leaving Add Screen")

    def add_entry(self):
        Logger.info("Adding new dictionary entry")
        if self.has_no_empty_fields():
            try:
                new_dict_entry = db_helper.Dictionary(
                    tagalog=self.ids.t_input.text,
                    kapampangan=self.ids.k_input.text.lower(),
                    english=self.ids.e_input.text,
                )
                db_helper.session.add(new_dict_entry)
                db_helper.session.commit()

                self.popup("Confirmation Message", "Dictionary entry saved!")
                self.clear_text_inputs()

                Logger.info("Application: {} added.".format(new_dict_entry.kapampangan))
            except IntegrityError as e:
                self.popup("Error Message", "Entry already exists!")
                db_helper.session.rollback()
                self.clear_text_inputs()
                Logger.error("Application: Error Stack: {}".format(e))
        else:
            self.popup("Error Message", "All the fields are mandatory!")
            Logger.info("Application: User Error: All the fields are mandatory!")

    def popup(self, title, message):
        # Generic popup for error and confirmation messages
        content = Label(text=message, font_size=40, color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title, content=content, size_hint=(0.6, 0.3))
        popup.open()

    def has_no_empty_fields(self):
        if all([self.ids.e_input.text, self.ids.k_input.text, self.ids.t_input.text]):
            return True
        return False


class DictInput(DictTextInput):
    pass

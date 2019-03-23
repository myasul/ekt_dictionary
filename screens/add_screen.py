from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.lang import Builder
import os
from sqlalchemy.exc import IntegrityError
from model import database_helper as db_helper
from components.components import AutoDismissPopup, DictTextInput

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/add_screen.kv")


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

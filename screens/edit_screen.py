from sqlalchemy.exc import SQLAlchemyError

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.properties import StringProperty

import model.database_helper as db_helper
from components.components import DictTextInput, AutoDismissPopup

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
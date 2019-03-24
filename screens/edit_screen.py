from sqlalchemy.exc import SQLAlchemyError
import os

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock

import model.database_helper as db_helper
from components.components import DictTextInput, AutoDismissPopup

path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/../kv/edit_screen.kv")


class EditScreen(Screen):
    def __init__(self, **kwargs):
        super(EditScreen, self).__init__(**kwargs)
        self.kapampangan = StringProperty()
        self.tagalog = StringProperty()
        self.english = StringProperty()
        self.db_object = None

    def on_pre_enter(self):
        Logger.info('Application: Entering Edit Screen')
        Logger.info('Application: Editing: K: {} - E: {} - T: {}'.format(
            self.kapampangan, self.english, self.tagalog))
        self.set_text_from_dict_val()

    def on_pre_leave(self):
        Logger.info('Application: Leaving Edit Screen')

    def set_text_from_dict_val(self):
        self.ids.kapampangan_es.text = self.kapampangan
        self.ids.tagalog_es.text = self.tagalog
        self.ids.english_es.text = self.english

    def set_dict_val_from_text(self):
        self.kapampangan = self.ids.kapampangan_es.text
        self.tagalog = self.ids.tagalog_es.text
        self.english = self.ids.english_es.text

    def on_save(self):
        Logger.info(
            'Application: Saving changes for {}'.format(self.kapampangan))
        if self.db_object:
            try:
                # Extract new values from text fields
                self.set_dict_val_from_text()

                # Save the extracted values
                self.db_object.kapampangan = self.kapampangan
                self.db_object.tagalog = self.tagalog
                self.db_object.english = self.english

                db_helper.session.add(self.db_object)
                db_helper.session.commit()

                Logger.info(
                    'Application: Changes for {} is now saved'.format(
                        self.kapampangan))

                # Multiple delays are in place to display
                # all information needed simultaneously
                self.popup('Confirmation Message',
                           'Changes saved!')
                Clock.schedule_once(self.go_to_dict_screen, 1.5)
            except SQLAlchemyError as e:
                Logger.error('Application: Error Stack: {}'.format(e))
                db_helper.session.rollback()
                Logger.error('Dictionary entry\'s object is missing')
                self.popup('Error Message', 'Error occured. Please report.')
        else:
            Logger.error('Dictionary entry\'s object is missing')
            self.popup('Error Message', 'Error occured. Please report.')

    def go_to_dict_screen(self, *args):
        self.update_dict_screen()
        self.manager.current = 'dict_entry'

    def update_dict_screen(self):
        # Dicionary screen's text fields should be up-to-date
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
            Logger.error('Application: Error Stack: {}'.format(error))
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

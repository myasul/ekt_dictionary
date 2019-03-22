from sqlalchemy.exc import SQLAlchemyError

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty

from components.components import DeletePopup, AutoDismissPopup
import model.database_helper as db_helper

class DictScreen(Screen):
    def __init__(self, **kwargs):
        super(DictScreen, self).__init__(**kwargs)
        self.kapampangan = StringProperty()
        self.tagalog = StringProperty()
        self.english = StringProperty()
        self.back_screen = StringProperty()
        self.db_object = None

    def set_dict_entry(self, entry):
        self.db_object = entry
        self.kapampangan = entry.kapampangan
        self.tagalog = entry.tagalog
        self.english = entry.english

    def on_pre_enter(self):
        # Populate the Labels with the data retrieved from database
        if self.kapampangan:
            print("ENTERED DICT SCREEN!")
            entry = self.get_entry()

            if not entry:
                self.popup('Error Message', 'Error occured. Please report.')
                return

            self.set_dict_entry(entry)
            self.ids.kapampangan_ds.text = self.kapampangan
            self.ids.tagalog_ds.text = self.tagalog
            self.ids.english_ds.text = self.english
        else:
            # TODO :: Add logging
            self.popup('Error Message', 'Error occured. Please report.')

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
            db_helper.session.delete(entry)
            try:
                db_helper.session.commit()
                # Multiple delays are in place to display
                # all information needed simultaneously
                self.popup('Confirmation Message',
                           'Dictionary entry deleted!')
                Clock.schedule_once(self.on_back, 1.5)
            except SQLAlchemyError as e:
                # TODO :: Add logging
                print("Error: {}".format(e))
                db_helper.session.rollback()
                self.popup('Error Message', 'Error occured. Please report.')
        else:
            # TODO :: Add logging
            self.popup('Error Message', 'Error occured. Please report.')

    def on_edit_entry(self):
        # Retrieve Edit Screen
        screen_manager = App.get_running_app().root
        edit_entry = screen_manager.get_screen('edit_entry')

        # Populate Edit Screen's class variables
        edit_entry.kapampangan = self.kapampangan
        edit_entry.tagalog = self.tagalog
        edit_entry.english = self.english
        edit_entry.db_object = self.db_object

        # Redirect to Edit Screen
        screen_manager.current = 'edit_entry'

    def on_back(self, *args):
        self.manager.current = self.back_screen

    def go_to_list_screen(self, *args):
        self.manager.current = 'list'

    def get_entry(self):
        # Get dictionary data using the word selected
        # by the user from the List Screen
        entry, error = db_helper.search_entry(
            kapampangan=self.kapampangan,
            english=self.english,
            tagalog=self.tagalog)
        if error:
            # TODO :: Add logging
            return None
        return entry

    def popup(self, title, message):
        # Generic popup for error and confirmation messages
        content = Label(text=message,
                        font_size=20,
                        color=[1, 1, 1, 1])
        popup = AutoDismissPopup(title=title,
                                 content=content,
                                 size_hint=(0.4, 0.2))
        popup.open()
# Imports from SQLite library
from sqlalchemy import create_engine, asc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from database_setup import Dictionary, Base

# Imports from Kivy library
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Rectangle, Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'fullscreen', 0)


# Connect to the database and create a database session
engine = create_engine('sqlite:///ekt_dictionary.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class AddScreen(Screen):
    def clear_text_inputs(self):
        self.ids.e_input.text = ''
        self.ids.k_input.text = ''
        self.ids.t_input.text = ''

    def add_entry(self):
        # TODO :: Make the error message's box size dynamic
        content = ErrorLabel(text='',
                             font_size=25,
                             color=[1, 0, 0, 1])
        content.bind(text=content.on_text)
        popup = Popup(title='Error Message',
                      content=content,
                      size=[500, 300],
                      size_hint=(None, None))

        try:
            if not self.are_fields_empty():
                new_dict_entry = Dictionary(tagalog=self.ids.t_input.text,
                                            kapampangan=self.ids.k_input.text,
                                            english=self.ids.e_input.text)
                session.add(new_dict_entry)
                session.commit()
                popup.title = 'Confirmation Message'
                popup.content.text = 'Dictionary entry saved!'
                popup.open()
                self.clear_text_inputs()
            else:
                content.text = 'All text fields should be populated.'
                popup.open()
        except IntegrityError:
            popup.content.text = 'Entry already exists.'
            popup.open()
            session.rollback()
            self.clear_text_inputs()

    def are_fields_empty(self):
        if not all([self.ids.e_input.text,
                    self.ids.k_input.text,
                    self.ids.t_input.text]):
            return True
        return False


class ErrorLabel(Label):
    # TODO :: Make the error message's box size dynamic
    def on_text(self, instance, value):
        self.size = self.texture_size


class SearchScreen(Screen):
    pass


class ListScreen(Screen):
    def on_pre_enter(self):
        all_entries = self.show_all_entries()
        row_num = len(all_entries)

        self.ids.list_grid.rows = row_num
        for entry in all_entries:
            self.ids.list_grid.add_widget(
                DictEntry(
                    text=entry.kapampangan,
                    font_size=25,
                )
            )

    def on_leave(self):
        delete_widgets = []
        for widget in self.ids.list_grid.children:
            if isinstance(widget, DictEntry):
                delete_widgets.append(widget)

        for widget in delete_widgets:
            self.ids.list_grid.remove_widget(widget)

    def show_all_entries(self):
        try:
            return session.query(Dictionary) \
                .order_by(Dictionary.kapampangan.asc()) \
                .all()
        except IntegrityError:
            # TODO :: Add logging
            content = ErrorLabel(text='Error occured. Please report.',
                                 font_size=25,
                                 color=[1, 0, 0, 1])
            popup = Popup(title='Error Message',
                          content=content,
                          size=[500, 300],
                          size_hint=(None, None))
            popup.open()
            return None


class DictEntry(Label):

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            print("{} clicked!".format(self.text))


class HomeScreen(Screen):
    pass


class MyScreenManager(ScreenManager):
    pass


ekt = Builder.load_file("ekt.kv")


class MainApp(App):
    def build(self):
        return ekt


if __name__ == "__main__":
    MainApp().run()

# Imports from SQLite library
from sqlalchemy import create_engine, asc, func, select, exc
from sqlalchemy.orm import sessionmaker
from database_setup import Dictionary, Base

# Imports from Kivy library
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
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
    def print_add_values(self):
        print("Tagalog entry: {}".format(self.ids.t_input.text))
        print("English entry: {}".format(self.ids.e_input.text))
        print("Kapampangan entry: {}".format(self.ids.k_input.text))

    def add_entry(self):
        new_dict_entry = Dictionary(tagalog=self.ids.t_input.text,
                                    kapampangan=self.ids.k_input.text,
                                    english=self.ids.e_input.text)
        session.add(new_dict_entry)
        session.commit()


class DictInput(TextInput):
    def on_enter(self):
        print("The value of Tagalog Text Input: {}".format(self.text))


class MyAnc(AnchorLayout):
    pass


class SearchScreen(Screen):
    pass


class ListScreen(Screen):
    pass


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

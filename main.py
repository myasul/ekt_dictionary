#!/usr/bin/env python3

# Kivy screens
from screens.add_screen import AddScreen
from screens.search_screen import SearchScreen
from screens.list_screen import ListScreen
from screens.dict_screen import DictScreen
from screens.edit_screen import EditScreen
from model import database_helper as db_helper
from tools.const import CSV_PATH, SCREENS_CSV, DICTIONARY_CSV, SCROLL_DIRECTION
from tools import helper

import re
import os

# Imports from Kivy library
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from kivy.logger import Logger
from components.borderbehaviour import BorderBehavior

Config.set("graphics", "width", "700")
Config.set("graphics", "height", "800")
Config.set("graphics", "fullscreen", 0)


class HomeScreen(Screen):
    def on_enter(self):
        Logger.info("Application: Entering Home Screen")
        if db_helper.count_dictionary_entries() == 0:
            # TODO :: Add pop-up to inform that the app is
            # populating database.
            helper.load_data(CSV_PATH + SCREENS_CSV, "screens")
            helper.load_data(CSV_PATH + DICTIONARY_CSV, "dictionary")
            helper.load_data(CSV_PATH + SCROLL_DIRECTION, "scroll_direction")
        else:
            Logger.info("Application: Dictionary database is loaded.")


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.id = "dict_sm"


path = os.path.dirname(os.path.abspath(__file__))
ekt = Builder.load_file(path + "/kv/ekt.kv")


class MainApp(App):
    title = "EKT Dictionary"

    def build(self):
        return ekt


if __name__ == "__main__":
    MainApp().run()

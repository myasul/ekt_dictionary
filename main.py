from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition


class AddScreen(Screen):
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


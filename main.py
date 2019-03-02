from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'fullscreen', 0)


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

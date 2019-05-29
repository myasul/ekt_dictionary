import os
from kivy.app import App
from kivy.uix.scrollview import ScrollView
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# Internal import
from components.borderbehaviour import BorderBehavior
from tools.const import MAX_ENTRIES, ROW_DEFAULT_HEIGHT
import model.database_helper as db_helper


class ScrollBorder(ScrollView, BorderBehavior):
    def __init__(self, screen_name, **kwargs):
        self.screen_name = screen_name
        super(ScrollBorder, self).__init__(**kwargs)

    def on_touch_up(self, touch):
        # TODO :: Add meaningful comments
        if self.scroll_y <= 0:
            self.populate_with_additional_entries()
        return super().on_touch_up(touch)

    def populate_with_additional_entries(self):
        # TODO :: Add meaningful comments
        screen_manager = App.get_running_app().root
        screen = screen_manager.get_screen(self.screen_name)

        qr, error = db_helper.get_query_result()
        if isinstance(error, NoResultFound):
            return
        elif isinstance(error, MultipleResultsFound):
            db_helper.clean_query_result()
            return
        elif error:
            Logger.error(f"Application: Error Stack: {error}")
            screen.popup("Error Message", "Error Occured. Please report.")

        if qr.next_row < qr.total_rows:
            screen.do_search(
                next_row=qr.next_row,
                scroll=True,
            )

            self.scroll_y += self.recalculate_scroll_y(qr.next_row)

    def recalculate_scroll_y(self, next_row):
        y = (MAX_ENTRIES * ROW_DEFAULT_HEIGHT) / (ROW_DEFAULT_HEIGHT * next_row)
        return float(y)
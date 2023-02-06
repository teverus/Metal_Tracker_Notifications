from time import sleep

from Code.TeverusSDK.Screen import (
    Screen,
    Action,
    SCREEN_WIDTH,
    show_message,
)
from Code.TeverusSDK.Table import Table, WHITE


class SyncBandsWithPCloudScreen(Screen):
    def __init__(self):
        self.actions = [
            Action(function=self.print_hello_world, immediate_action=True, go_back=True)
        ]

        self.table = Table(
            table_title="Sync tracked bands with pCloud",
            table_width=SCREEN_WIDTH,
            rows_bottom_border=False,
            highlight=False,
        )

        super(SyncBandsWithPCloudScreen, self).__init__(self.table, self.actions)

    @staticmethod
    def print_hello_world():
        print(" Syncing bands... ")
        sleep(1)
        print(" Syncing bands... Done")
        show_message(("Bands synched with pCloud", WHITE))

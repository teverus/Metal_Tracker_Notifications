from Code.Screens.SyncBandsWithPCloudScreen import SyncBandsWithPCloudScreen
from Code.TeverusSDK.Screen import (
    Screen,
    Action,
    SCREEN_WIDTH,
    QUIT_ACTION,
    do_nothing,
)
from Code.TeverusSDK.Table import Table


class WelcomeScreen(Screen):
    def __init__(self):
        self.actions = [
            Action(
                name="Check new albums on metal-tracker.com",
                function=do_nothing,
            ),
            Action(
                name="Sync tracked bands with pCloud",
                function=SyncBandsWithPCloudScreen,
            ),
            Action(
                name="Add/remove tracked albums manually",
                function=do_nothing,
            ),
        ]

        self.table = Table(
            table_title="Metal-tracker.com notifications",
            rows=[action.name for action in self.actions],
            rows_bottom_border="-",
            table_width=SCREEN_WIDTH,
            footer=[QUIT_ACTION],
        )

        super(WelcomeScreen, self).__init__(self.table, self.actions)


if __name__ == "__main__":
    WelcomeScreen()

from Code.Screens.CheckNewAlbumsScreen import CheckNewAlbumsScreen
from Code.Screens.SeeAllBandsScreen import SeeAllBandsScreen
from Code.Screens.ShowNewAlbumsOnlyScreen import ShowNewAlbumsOnlyScreen
from Code.Screens.SyncBandsScreen import SyncBandsScreen
from Code.TeverusSDK.Screen import (
    Screen,
    Action,
    SCREEN_WIDTH,
    QUIT_ACTION,
)
from Code.TeverusSDK.Table import Table


class WelcomeScreen(Screen):
    def __init__(self):
        self.actions = [
            Action(
                name="Check new albums on metal-tracker.com",
                function=CheckNewAlbumsScreen,
            ),
            Action(
                name="See all bands",
                function=SeeAllBandsScreen,
            ),
            Action(
                name="Show new albums only",
                function=ShowNewAlbumsOnlyScreen,
            ),
            Action(
                name="Sync tracked bands with your music library",
                function=SyncBandsScreen,
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

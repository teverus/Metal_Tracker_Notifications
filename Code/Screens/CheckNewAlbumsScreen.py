from pathlib import Path

from Code.Modules.CheckNewAlbums import CheckNewAlbums
from Code.TeverusSDK.DataBase import DataBase
from Code.TeverusSDK.Screen import Screen, Action, SCREEN_WIDTH
from Code.TeverusSDK.Table import Table
from Code.TeverusSDK.YamlTool import YamlTool


class CheckNewAlbumsScreen(Screen):
    def __init__(self):
        self.database = DataBase(Path("Files/albums.db"))
        self.known_albums = self.database.read_table()
        self.bands = YamlTool(Path("Files/bands_list.yaml")).get_section("Bands")
        self.bands_number = len(self.bands)
        self.max_bands = len(str(self.bands_number))
        self.max_length = max([len(b) for b in self.bands])

        self.actions = [
            Action(
                function=CheckNewAlbums,
                arguments={"main": self},
                immediate_action=True,
                go_back=True,
            )
        ]

        self.table = Table(
            table_title="Checking new albums on metal-tracker.com",
            rows_bottom_border=False,
            highlight=False,
            table_width=SCREEN_WIDTH,
        )

        super(CheckNewAlbumsScreen, self).__init__(self.table, self.actions)

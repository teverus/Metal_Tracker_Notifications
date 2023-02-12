from math import ceil
from pathlib import Path

from Code.TeverusSDK.Screen import Screen, Action, SCREEN_WIDTH
from Code.TeverusSDK.Table import Table
from Code.TeverusSDK.YamlTool import YamlTool


class CheckNewAlbumsScreen(Screen):
    def __init__(self):
        self.actions = [
            Action(function=self.search_albums, immediate_action=True, go_back=True)
        ]

        self.table = Table(
            table_title="Checking new albums on metal-tracker.com",
            rows_bottom_border=False,
            highlight=False,
            table_width=SCREEN_WIDTH,
        )

        super(CheckNewAlbumsScreen, self).__init__(self.table, self.actions)

    @staticmethod
    def search_albums():
        bands = YamlTool(Path("Files/bands_list.yaml")).get_section("Bands")
        for index, band in enumerate(bands, 1):
            percentage = ceil(index / len(bands) * 100)
            print(f"[{index: 3}/{len(bands)}|{percentage: 3}%] {band}")
            ...

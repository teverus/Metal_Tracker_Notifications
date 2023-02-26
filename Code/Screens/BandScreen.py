from pathlib import Path

from Code.TeverusSDK.DataBase import DataBase
from Code.TeverusSDK.Screen import (
    Screen,
    SCREEN_WIDTH,
    GO_BACK_ACTION,
    Action,
    do_nothing,
)
from Code.TeverusSDK.Table import Table


class BandScreen(Screen):
    def __init__(self, band_name):
        self.band_name = band_name
        self.albums = self.get_albums()

        self.actions = [
            Action(name=album_name, function=do_nothing) for album_name in self.albums
        ]

        self.table = Table(
            table_title=band_name,
            rows=[action.name for action in self.actions],
            rows_bottom_border="-",
            table_width=SCREEN_WIDTH,
            footer=[GO_BACK_ACTION],
        )

        super(BandScreen, self).__init__(self.table, self.actions)

    def get_albums(self):
        df = DataBase(Path("Files/albums.db")).read_table()
        data = df.loc[df.Name == self.band_name][["Year", "Album"]]

        albums = []
        for index in range(len(data)):
            year, album = list(data.iloc[index])
            albums.append(f"[{year}] {album}")

        max_length = max([len(a) for a in albums])
        adjusted_albums = [a.ljust(max_length) for a in albums]
        sorted_albums = sorted(adjusted_albums, reverse=True)

        return sorted_albums

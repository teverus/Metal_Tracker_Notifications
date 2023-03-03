from pathlib import Path

from Code.AlbumEntry import AlbumEntry
from Code.Modules.ChangeAlbumStatus import change_album_status
from Code.Modules.OpenAlbumOnline import open_album_online
from Code.TeverusSDK.DataBase import DataBase
from Code.TeverusSDK.Screen import (
    Screen,
    SCREEN_WIDTH,
    GO_BACK_ACTION,
    Action,
)
from Code.TeverusSDK.Table import Table, ColumnWidth


class BandScreen(Screen):
    def __init__(self, band_name):
        self.band_name = band_name
        self.albums = self.get_albums()
        max_len = max([len(album.title) + 7 for album in self.albums])  # 7 is [XXXX]_

        self.actions = [
            [
                Action(
                    name=f"[{album.year}] {album.title.ljust(max_len)}",
                    function=open_album_online,
                    arguments={"album": album},
                ),
                Action(
                    name=album.listened,
                    function=change_album_status,
                    arguments={"main": self, "album": album},
                ),
            ]
            for album in self.albums
        ]

        self.table = Table(
            table_title=band_name,
            headers=["Album name", "Current status".center(35)],
            headers_upper="=",
            rows=[[column.name for column in row] for row in self.actions],
            rows_top_border=False,
            column_widths={0: ColumnWidth.FULL, 1: ColumnWidth.FIT},
            table_width=SCREEN_WIDTH,
            footer=[GO_BACK_ACTION],
        )

        super(BandScreen, self).__init__(self.table, self.actions)

    def get_albums(self):
        df = DataBase(Path("Files/albums.db")).read_table()
        data = df.loc[df.Name == self.band_name]
        data.sort_values(by="Year", ascending=False, inplace=True)

        albums = [AlbumEntry(*list(data.iloc[index])) for index in range(len(data))]

        return albums

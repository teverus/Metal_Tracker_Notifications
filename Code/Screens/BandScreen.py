import webbrowser
from pathlib import Path

from Code.AlbumEntry import AlbumEntry, NEW, CHECKED
from Code.TeverusSDK.DataBase import DataBase
from Code.TeverusSDK.Screen import (
    Screen,
    SCREEN_WIDTH,
    GO_BACK_ACTION,
    Action,
)
from Code.TeverusSDK.Table import Table, ColumnWidth

STATUS_TRANSITION = {NEW: CHECKED, CHECKED: NEW}


class BandScreen(Screen):
    def __init__(self, band_name):
        self.band_name = band_name
        self.albums = self.get_albums()
        max_len = max([len(album.title) + 7 for album in self.albums])  # 7 is [XXXX]_

        self.actions = [
            [
                Action(
                    name=f"[{album.year}] {album.title.ljust(max_len)}",
                    function=self.open_album_online,
                    arguments={"album": album},
                ),
                Action(
                    name=album.listened,
                    function=self.change_state,
                    arguments={"main": self, "album": album},
                ),
            ]
            for index, album in enumerate(self.albums)
        ]

        self.table = Table(
            table_title=band_name,
            headers=["Album name", "Current state".center(35)],
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

    @staticmethod
    def open_album_online(album):
        webbrowser.open(album.url)

    def change_state(self, main, album):
        self.change_value_on_backend(album)
        self.change_value_on_frontend(main, album)

    @staticmethod
    def change_value_on_backend(album):
        database = DataBase(Path("Files/albums.db"))
        df = database.read_table()

        album_entry = df.loc[df.URL == album.url]
        assert len(album_entry) == 1, "Found too many albums"
        target_db_index = album_entry.index.values[0]

        current_status = df.loc[target_db_index, "Status"]
        new_status = STATUS_TRANSITION[current_status]
        df.loc[target_db_index, "Status"] = new_status

        database.write_to_table(df)

    @staticmethod
    def change_value_on_frontend(main, album):
        indices = [i for i, r in enumerate(main.table.rows) if album.title in r[0]]
        assert len(indices) == 1, "Found too many indices"
        target_index = indices[0]

        current_status = main.table.rows[target_index][1]
        new_status = STATUS_TRANSITION[current_status]
        main.table.rows[target_index][1] = new_status

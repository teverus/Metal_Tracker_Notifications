from Code.AlbumEntry import NEW, AlbumEntry
from Code.Modules.ChangeAlbumStatus import change_album_status
from Code.Modules.OpenAlbumOnline import open_album_online
from Code.TeverusSDK.Screen import (
    Screen,
    SCREEN_WIDTH,
    GO_BACK_ACTION,
    Action,
)
from Code.TeverusSDK.Table import Table, ColumnWidth
from Code.constants import DATABASE


class ShowNewAlbumsOnlyScreen(Screen):
    def __init__(self):
        self.database = DATABASE
        self.df = self.database.read_table()
        self.new_albums = self.get_new_albums()
        max_band = max([len(a.band) for a in self.new_albums])
        max_title = max([len(a.title) for a in self.new_albums])
        self.actions = [
            [
                Action(
                    name=f"{album.band.rjust(max_band)} [{album.year}] {album.title.ljust(max_title)}",
                    function=open_album_online,
                    arguments={"album": album},
                ),
                Action(
                    name=album.listened,
                    function=change_album_status,
                    arguments={"main": self, "album": album, "remove_band": True},
                ),
            ]
            for album in self.new_albums
        ]

        self.table = Table(
            table_title="New albums ",
            headers=["Album name", "Current status".center(35)],
            rows=[[column.name for column in row] for row in self.actions],
            rows_top_border=False,
            table_width=SCREEN_WIDTH,
            column_widths={0: ColumnWidth.FULL, 1: ColumnWidth.FIT},
            max_rows=34,
            footer=[GO_BACK_ACTION],
        )
        super(ShowNewAlbumsOnlyScreen, self).__init__(self.table, self.actions)

    def get_new_albums(self):
        data = self.df.loc[self.df.Status == NEW]
        albums = [AlbumEntry(*list(data.iloc[index])) for index in range(len(data))]

        return albums

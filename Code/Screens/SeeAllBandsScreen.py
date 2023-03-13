from pathlib import Path

from Code.Screens.BandScreen import BandScreen
from Code.TeverusSDK.DataBase import DataBase
from Code.TeverusSDK.Screen import (
    Screen,
    SCREEN_WIDTH,
    GO_BACK_ACTION,
    Action,
    do_nothing,
)
from Code.TeverusSDK.Table import Table


def divide_into_columns(items, max_rows):
    result = []
    processed_items = 0

    while processed_items < len(items):
        for row in range(max_rows):
            if len(result) >= max_rows:
                target_index = processed_items - max_rows
                goes_beyond = processed_items >= len(items)

                item_to_add = "" if goes_beyond else items[processed_items]
                result[target_index].append(item_to_add)

            else:
                result.append([items[processed_items]])

            processed_items += 1

    return result


class SeeAllBandsScreen(Screen):
    def __init__(self):
        self.database = DataBase(Path("Files/albums.db"))
        self.df = self.database.read_table()

        self.bands = sorted(set(list(self.df.Name)))
        self.bands = divide_into_columns(self.bands, max_rows=37)

        self.actions = [
            [
                Action(
                    function=BandScreen if band else do_nothing,
                    arguments={"band_name": band},
                )
                for band in band_group
            ]
            for band_group in self.bands
        ]

        self.table = Table(
            table_title="All bands",
            rows=self.bands,
            footer=[GO_BACK_ACTION],
            table_width=SCREEN_WIDTH,
            max_rows=37,
        )

        super(SeeAllBandsScreen, self).__init__(self.table, self.actions)

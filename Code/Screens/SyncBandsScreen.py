import os
from pathlib import Path

from Code.TeverusSDK.Screen import (
    Screen,
    Action,
    SCREEN_WIDTH,
    show_message,
)
from Code.TeverusSDK.Table import Table, WHITE
from Code.TeverusSDK.YamlTool import YamlTool


class SyncBandsScreen(Screen):
    def __init__(self):
        self.actions = [
            Action(
                function=self.sync_bands_with_music_library,
                immediate_action=True,
                go_back=True,
            )
        ]

        self.table = Table(
            table_title="Sync tracked bands with your music library",
            table_width=SCREEN_WIDTH,
            rows_bottom_border=False,
            highlight=False,
        )

        super(SyncBandsScreen, self).__init__(self.table, self.actions)

    @staticmethod
    def sync_bands_with_music_library():
        library_path = Path(r"O:\МУЗЫКА")
        excluded = ["Разное"]

        all_directories = [f for _, f, _ in os.walk(library_path)][0]
        bands = [d for d in all_directories if " OST" not in d if d not in excluded]

        print(f" Bands in your music library: {len(bands)}")
        YamlTool(Path("Files/bands_list.yaml")).save_yaml({"Bands": bands})
        print(" Syncing bands... Done")
        show_message(("Bands list is now synched with your music library", WHITE))

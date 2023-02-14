from pathlib import Path

from playwright.sync_api import sync_playwright

from Code.TeverusSDK.Screen import Screen, Action, SCREEN_WIDTH, show_message
from Code.TeverusSDK.Table import Table, WHITE
from Code.TeverusSDK.YamlTool import YamlTool

METAL_TRACKER_SEARCH_URL = "https://www.metal-tracker.com/torrents/search.html"


class CheckNewAlbumsScreen(Screen):
    def __init__(self):
        self.actions = [
            Action(
                function=self.search_albums,
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

    def search_albums(self):
        with sync_playwright() as p:
            print(" Starting browser...")
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            page.goto(METAL_TRACKER_SEARCH_URL, wait_until="domcontentloaded")
            print(" Starting browser... Done")

            bands = YamlTool(Path("Files/bands_list.yaml")).get_section("Bands")
            bands_number = len(bands)
            max_bands = len(str(bands_number))
            max_length = max([len(b) for b in bands])

            for index, band in enumerate(bands, 1):
                page.locator("//input[@id='searchBox']").type(band)
                page.locator("//input[@name='go-search']").click()
                page.wait_for_load_state()
                found_albums = page.locator("//div[@class='smallalbum']").all()
                valid_albums = self.check_albums(found_albums, band)

                percentage = str(int(index / bands_number * 100)).rjust(3)
                info = f"{str(index).rjust(max_bands)}/{bands_number}|{percentage}%"
                band_adjusted = str(band).ljust(max_length)
                print(f" [{info}] {band_adjusted} {'#' * len(valid_albums)}")

            show_message("All albums were processed", WHITE)

    @staticmethod
    def check_albums(found_albums, target_name):
        valid_albums = []

        for album in found_albums:
            album_name = album.inner_text().split("\n")[0]
            if album_name.lower().startswith(f"{target_name.lower()} - "):
                valid_albums.append(album_name)

        return valid_albums

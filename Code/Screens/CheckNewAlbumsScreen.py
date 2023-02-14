from pathlib import Path

from playwright.sync_api import sync_playwright

from Code.TeverusSDK.Screen import Screen, Action, SCREEN_WIDTH, show_message
from Code.TeverusSDK.Table import Table, WHITE
from Code.TeverusSDK.YamlTool import YamlTool

METAL_TRACKER_SEARCH_URL = "https://www.metal-tracker.com/torrents/search.html"


class CheckNewAlbumsScreen(Screen):
    def __init__(self):
        self.found_albums = None
        self.page = None
        self.band = None
        self.index = None
        self.valid_albums = None
        self.max_length = None
        self.max_bands = None
        self.bands_number = None

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
        with sync_playwright() as self.p:
            print(" Starting browser...")
            self.page = self.get_page()
            self.page.goto(METAL_TRACKER_SEARCH_URL, wait_until="domcontentloaded")
            print(" Starting browser... Done")

            bands = YamlTool(Path("Files/bands_list.yaml")).get_section("Bands")
            self.bands_number = len(bands)
            self.max_bands = len(str(self.bands_number))
            self.max_length = max([len(b) for b in bands])

            for index, band in enumerate(bands, 1):
                self.index = index
                self.band = band

                self.search_for_albums()
                self.check_found_albums()
                self.show_info()

            show_message("All albums were processed", WHITE)

    def get_page(self, headless=True):
        browser = self.p.firefox.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        return page

    def search_for_albums(self):
        self.page.locator("//input[@id='searchBox']").type(self.band)
        self.page.locator("//input[@name='go-search']").click()
        self.page.wait_for_load_state()
        self.found_albums = self.page.locator("//div[@class='smallalbum']").all()

    def check_found_albums(self):
        self.valid_albums = []

        for album in self.found_albums:
            album_name = album.inner_text().split("\n")[0]
            if album_name.lower().startswith(f"{self.band.lower()} - "):
                self.valid_albums.append(album_name)

    def show_info(self):
        percent = str(int(self.index / self.bands_number * 100)).rjust(3)
        info = f"{str(self.index).rjust(self.max_bands)}/{self.bands_number}|{percent}%"
        band_adjusted = str(self.band).ljust(self.max_length)
        print(f" [{info}] {band_adjusted} {'#' * len(self.valid_albums)}")

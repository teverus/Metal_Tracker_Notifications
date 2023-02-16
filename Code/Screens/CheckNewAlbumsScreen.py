from pathlib import Path
from time import sleep

from playwright.sync_api import sync_playwright

from Code.TeverusSDK.Screen import Screen, Action, SCREEN_WIDTH, show_message
from Code.TeverusSDK.Table import Table, WHITE
from Code.TeverusSDK.YamlTool import YamlTool

METAL_TRACKER_SEARCH_URL = "https://www.metal-tracker.com/torrents/search.html"


class CheckNewAlbumsScreen(Screen):
    def __init__(self):
        self.bands = YamlTool(Path("Files/bands_list.yaml")).get_section("Bands")
        self.bands_number = len(self.bands)
        self.max_bands = len(str(self.bands_number))
        self.max_length = max([len(b) for b in self.bands])
        self.found_albums = None
        self.page = None
        self.band = None
        self.index = None
        self.valid_albums = None

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
            print(" Opening metal-tracker.com...")
            self.page = self.get_page(False)
            self.page.goto(METAL_TRACKER_SEARCH_URL)
            print(" Opening metal-tracker.com... Done")

            for index, band in enumerate(self.bands[45:], 1):
                self.index = index
                self.band = band

                self.search_for_albums()
                self.set_country_if_needed()
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
            found_name = album_name.split(" - ")[0]

            several_artists = "/" in found_name or "," in found_name
            if several_artists:
                character = "/" if "/" in found_name else ","
                artist_name = self.split_and_check(found_name, character)
                ...
            # else:
            #     ...
            # if "/" in found_name:
            #     artist_name = self.split_and_check(found_name, "/")
            # elif "," in found_name:
            #     artist_name = self.split_and_check(found_name, ",")
            # elif " " in found_name and " " not in self.band:
            #     artist_name = self.split_and_check(found_name, " ")
            else:
                artist_name = found_name

            # --- For debugging --------------------------------------------------------
            # actual_name = artist_name
            # expect_name_ = self.band
            # is_valid = artist_name == self.band
            # --------------------------------------------------------------------------

            if artist_name == self.band:
                self.valid_albums.append(album_name)
                # TODO Проверять на включение в базу

    def split_and_check(self, album_artist_name, character):
        artists = album_artist_name.split(character)
        for artist in artists:
            artist = artist.strip()
            if artist == self.band:
                return artist

        return []

    def show_info(self):
        percent = str(int(self.index / self.bands_number * 100)).rjust(3)
        info = f"{str(self.index).rjust(self.max_bands)}/{self.bands_number}|{percent}%"
        band_adjusted = str(self.band).ljust(self.max_length)
        print(f" [{info}] {band_adjusted} {'#' * len(self.valid_albums)}")

    def set_country_if_needed(self):
        if len(self.found_albums) == 12:
            selector = self.page.locator("//select[@id='SearchTorrentsForm_country']")
            selector.select_option("4")
            self.page.locator("//input[@id='submitForm']").click()
            found_albums_old = self.found_albums[0].inner_text()
            for _ in range(10):
                self.found_albums = self.page.locator(
                    "//div[@class='smallalbum']"
                ).all()
                found_albums_new = self.found_albums[0].inner_text()
                if found_albums_new != found_albums_old:
                    break
                sleep(1)
            ...

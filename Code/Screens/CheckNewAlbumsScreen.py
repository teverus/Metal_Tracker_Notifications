import re
from datetime import datetime
from pathlib import Path
from time import sleep

from pandas import DataFrame
from playwright.sync_api import sync_playwright

from Code.TeverusSDK.DataBase import DataBase
from Code.TeverusSDK.Screen import Screen, Action, SCREEN_WIDTH, show_message
from Code.TeverusSDK.Table import Table, WHITE
from Code.TeverusSDK.YamlTool import YamlTool

HOST = "https://www.metal-tracker.com"
METAL_TRACKER_SEARCH_URL = f"{HOST}/torrents/search.html"
URL = "URL"
BAND_NAME = "Name"
COLUMNS = [BAND_NAME, "Album", "Year", URL, "Listened"]
KNOWN = "known"
NEW = "new"


class CheckNewAlbumsScreen(Screen):
    def __init__(self):
        self.database = DataBase(Path("Files/albums.db"))
        self.known_albums = self.database.read_table()
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
            Action(function=self.check_new_albums, immediate_action=True, go_back=True)
        ]

        self.table = Table(
            table_title="Checking new albums on metal-tracker.com",
            rows_bottom_border=False,
            highlight=False,
            table_width=SCREEN_WIDTH,
        )

        super(CheckNewAlbumsScreen, self).__init__(self.table, self.actions)

    def check_new_albums(self):
        with sync_playwright() as self.p:
            time_start = datetime.now()
            print(" Opening metal-tracker.com...")
            self.page = self.get_page()
            for _ in range(3):
                try:
                    self.page.goto(METAL_TRACKER_SEARCH_URL)
                    break
                except Exception:
                    print(" Trying once again...")
                    sleep(1)
            else:
                raise Exception(f"\n[ERROR] Couldn't open {METAL_TRACKER_SEARCH_URL}")

            print(" Opening metal-tracker.com... Done")

            for index, band in enumerate(self.bands, 1):
                self.index = index
                self.band = band

                self.search_for_albums()
                self.check_found_albums()
                self.show_info()

            time_finish = datetime.now()
            time_diff = str(time_finish - time_start).split(".")[0]
            show_message(f"All albums were processed in {time_diff}", WHITE)

    def get_page(self, headless=True):
        browser = self.p.firefox.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        return page

    def search_for_albums(self):
        search_input = "//input[@id='SearchTorrentsForm_nameTorrent']"
        country = "//select[@id='SearchTorrentsForm_country']"
        finland = "4"
        search_button = "//input[@id='submitForm']"

        self.page.locator(search_input).clear()
        self.page.locator(search_input).type(self.band)
        self.page.locator(country).select_option(finland)
        self.page.locator(search_button).click()
        self.page.wait_for_load_state("networkidle")
        sleep(2)

        self.found_albums = self.page.locator("//div[@class='smallalbum']").all()

    def check_found_albums(self):
        self.valid_albums = {KNOWN: 0, NEW: 0}

        for album in self.found_albums:
            info = album.inner_text()
            artist_and_album_title = info.split("\n")[0]

            # --- Band -----------------------------------------------------------------
            artist_name = self.get_artist_name(artist_and_album_title)

            if artist_name == self.band:
                # --- Album ------------------------------------------------------------
                album_title = re.findall(r" - (.*)", artist_and_album_title)[0]

                # --- Year -------------------------------------------------------------
                YEAR = "Год: "
                year = info.split(YEAR)[-1].split("\n")[0] if YEAR in info else "---"

                # --- Url --------------------------------------------------------------
                unique_part = album.locator("//a").first.get_attribute("href")
                full_url = f"{HOST}{unique_part}"

                # --- Check if album exists in DB --------------------------------------
                album_exists = self.database.check_if_value_exists(full_url, "URL")

                # --- Add to DB if needed ----------------------------------------------
                if not album_exists:
                    df = DataFrame([], columns=COLUMNS)
                    df.loc[0] = [artist_name, album_title, year, full_url, "0"]
                    self.database.append_to_table(df, sort_by=BAND_NAME)

                # --- Add to self.valid_albums for indication --------------------------
                target_key = KNOWN if album_exists else NEW
                self.valid_albums[target_key] += 1

    def get_artist_name(self, artist_and_album_title):
        name = artist_and_album_title.split(" - ")[0]
        name = name.replace("...", "") if "..." in name else name

        delimiters = [char for char in ["/", ",", "&"] if char in name]
        if delimiters:
            assert len(delimiters) == 1, f"{delimiters = }"
            artist_name = self.split_and_check(name, delimiters[0])
        else:
            artist_name = name

        return artist_name

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
        known_albums = "#" * self.valid_albums[KNOWN]
        new_albums = "!" * self.valid_albums[NEW]
        print(f" [{info}] {band_adjusted} {new_albums}{known_albums}")

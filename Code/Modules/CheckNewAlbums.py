import re
from datetime import datetime
from time import sleep

from pandas import DataFrame
from playwright.sync_api import sync_playwright

from Code.AlbumEntry import AlbumEntry
from Code.TeverusSDK.Screen import show_message, SCREEN_WIDTH, wait_for_enter
from Code.TeverusSDK.Table import WHITE, Table

HOST = "https://www.metal-tracker.com"
METAL_TRACKER_SEARCH_URL = f"{HOST}/torrents/search.html"
URL = "URL"
BAND_NAME = "Name"
COLUMNS = [BAND_NAME, "Album", "Year", URL, "Status"]
KNOWN = "known"
NEW = "new"


class CheckNewAlbums:
    def __init__(self, main):
        # --- VARIABLES ----------------------------------------------------------------
        self.time_start = datetime.now()
        self.page = None
        self.found_albums = None
        self.main = main
        self.database = self.main.database
        self.max_bands = self.main.max_bands
        self.bands_number = self.main.bands_number
        self.max_length = self.main.max_length
        self.new_albums = []

        # --- MAIN ACTION --------------------------------------------------------------
        with sync_playwright() as self.p:
            self.open_metal_tracker()

            for index, band in enumerate(self.main.bands, 1):
                self.index = index
                self.band = band

                self.search_for_albums()
                self.check_found_albums()
                self.show_info()

            msg = "Check new albums" if self.new_albums else "All albums were processed"
            show_message(
                message=msg,
                color=WHITE,
                need_confirmation=False,
            )

            half = int((SCREEN_WIDTH - 8) / 2)
            if self.new_albums:
                print(" ")
                [
                    print(f"{album.band.rjust(half)} [{album.year}] {album.title}")
                    for album in self.new_albums
                ]

            wait_for_enter()

    ####################################################################################
    #    HELPERS                                                                       #
    ####################################################################################

    def open_metal_tracker(self):
        print(" Opening metal-tracker.com...")
        self.page = self.get_page()
        for _ in range(3):
            try:
                self.page.goto(METAL_TRACKER_SEARCH_URL, wait_until="domcontentloaded")
                break
            except Exception:
                print(" Trying once again...")
                sleep(1)
        else:
            raise Exception(f"\n[ERROR] Couldn't open {METAL_TRACKER_SEARCH_URL}")

        print(" Opening metal-tracker.com... Done")

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
        self.page.wait_for_load_state("domcontentloaded")
        sleep(2)

        self.found_albums = self.page.locator("//div[@class='smallalbum']").all()

    def check_found_albums(self):
        for album in self.found_albums:
            info = album.inner_text()

            artist_and_album_title = info.split("\n")[0]
            entry = AlbumEntry()

            # --- Band -----------------------------------------------------------------
            entry.band = self.get_artist_name(artist_and_album_title)

            if entry.band == self.band:
                # --- Album ------------------------------------------------------------
                entry.title = re.findall(r" - (.*)", artist_and_album_title)[0]

                # --- Year -------------------------------------------------------------
                YEAR = "Год: "
                result = info.split(YEAR)[-1].split("\n")[0] if YEAR in info else "----"
                entry.year = result

                # --- Url --------------------------------------------------------------
                unique_part = album.locator("//a").first.get_attribute("href")
                entry.url = f"{HOST}{unique_part}"

                # --- Check if album exists in DB --------------------------------------
                album_exists = self.database.check_if_value_exists(entry.url, "URL")

                # --- Add to DB if needed ----------------------------------------------
                if not album_exists:
                    df = DataFrame([], columns=COLUMNS)
                    df.loc[0] = [entry.band, entry.title, entry.year, entry.url, "New"]
                    self.database.append_to_table(df, sort_by=BAND_NAME)

                    self.new_albums.append(entry)

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
        time_elapsed = str(datetime.now() - self.time_start).split(".")[0]

        percent_done = int(self.index / self.main.bands_number * 100)
        percent_free = 100 - percent_done
        taken = "#" * percent_done
        empty = "." * percent_free
        load_bar = f"{time_elapsed} [{taken}{empty}] {percent_done:2} %"

        Table(
            table_title="Checking new albums on metal-tracker.com",
            table_width=SCREEN_WIDTH,
            rows=load_bar,
            rows_bottom_border=False,
        ).print_table()

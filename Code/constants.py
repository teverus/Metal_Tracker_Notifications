from pathlib import Path

from Code.TeverusSDK.DataBase import DataBase

DATABASE = DataBase(Path("Files/albums.db"))
ERROR_START = "=== ERROR ==========================="
ERROR_END = "====================================="

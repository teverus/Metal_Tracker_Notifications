from pathlib import Path
from sqlite3 import connect
from typing import Union

from pandas import DataFrame
import pandas as pd


class DataBase:
    def __init__(self, path_to_database: Path):
        """
        [path_to_database]
            * Use Path from pathlib
            * Path must lead from root
            * Path must include filename and its extension
            * example: Path("Files/GameReleases.db")
        """
        self.path_to_db = path_to_database
        self.connection = connect(self.path_to_db)
        self.table_name = path_to_database.stem

    @property
    def table(self):
        return self.read_table()

    # === CREATE =======================================================================
    @classmethod
    def create_database_with_columns(
        cls,
        path_to_directory: Path,
        database_name: str,
        columns: list,
    ):
        path = path_to_directory / f"{database_name}.db"
        connection = connect(path)
        assert path.exists()

        dataframe = DataFrame([], columns=columns)
        dataframe.to_sql(database_name, connection, index=False, if_exists="replace")

    # === READ =========================================================================
    def read_table(self) -> DataFrame:
        data = pd.read_sql(f"select * from {self.table_name}", self.connection)

        return data

    def check_if_value_exists(self, value, column):
        table = self.table
        result = bool(len(table.loc[table[column] == value]))

        return result

    # === UPDATE =======================================================================
    def write_to_table(self, df: DataFrame):
        df.to_sql(self.table_name, self.connection, index=False, if_exists="replace")

        self.connection = connect(self.path_to_db)

    def append_to_table(self, df: DataFrame, sort_by=False):
        result = pd.concat([self.table, df], ignore_index=True)

        if sort_by:
            result.sort_values(by=sort_by, inplace=True, ignore_index=True)

        self.write_to_table(result)

    # === DELETE =======================================================================
    def remove_by_index(self, index: Union[int, list]):
        """
        [index]
            * Can be a single index or a list of indices
        """
        index = [index] if not isinstance(index, list) else index

        self.table.drop(index=index, inplace=True)

        self.write_to_table(self.table)

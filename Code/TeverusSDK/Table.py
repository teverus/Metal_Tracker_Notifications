import os
from math import ceil
from typing import Union

import bext
from colorama import Back, Fore

WHITE = Back.WHITE + Fore.BLACK
RED = Back.RED + Fore.WHITE
GREEN = Back.GREEN + Fore.WHITE
BLUE = Back.BLUE + Fore.WHITE

END_HIGHLIGHT = Back.BLACK + Fore.WHITE


class ColumnWidth:
    FULL = "Full"
    FIT = "Fit"


class Table:
    def __init__(
        self,
        # Headers
        headers: list = None,
        headers_top_border="=",
        headers_upper=True,
        headers_centered=True,
        # Rows
        rows: Union[list[str] | list[list[str]]] = None,
        rows_top_border="=",
        rows_bottom_border="=",
        rows_centered=True,
        rows_highlight=None,
        # Table title
        table_title="",
        table_title_centered=True,
        table_title_caps=True,
        table_title_top_border="=",
        # Footer
        footer=None,
        footer_centered=True,
        footer_bottom_border="=",
        # General table
        table_width=None,
        highlight=None,
        current_page=1,
        max_rows=None,
        max_columns=None,
        column_widths=None,
        clear_console=True,
        show_cursor=False,
    ):
        # Internal use only
        self.side_padding_length = 2
        self.wall_length = 3

        # Table title
        self.table_title = table_title
        self.table_title_top_border = table_title_top_border
        self.table_title_centered = table_title_centered
        self.table_title_caps = table_title_caps

        # Headers
        self.headers = headers
        self.headers_top_border = headers_top_border
        self.headers_upper = headers_upper
        self.headers_centered = headers_centered

        # Rows
        self.rows = self.get_rows(rows)
        self.rows_top_border = rows_top_border
        self.rows_bottom_border = rows_bottom_border
        self.rows_centered = rows_centered
        self.rows_highlight = rows_highlight

        # Footer
        self.footer = footer
        self.footer_bottom_border = footer_bottom_border
        self.footer_centered = footer_centered

        # General table
        self.highlight = highlight
        self.clear_console = clear_console
        self.show_cursor = show_cursor
        self.current_page = current_page
        self.max_rows = self.get_max_rows(max_rows)
        self.max_columns = self.get_max_columns(max_columns)
        self.has_multiple_pages = self.get_multiple_pages()
        self.max_page = self.get_max_page()
        self.cage = self.get_cage()

        # Calculated values
        self.walls_length = self.get_walls_length()
        self.visible_rows = self.get_visible_rows()
        self.table_width = self.get_table_width(table_width)
        self.column_widths = self.get_column_widths(column_widths)

    ####################################################################################
    #    PRINT TABLE                                                                   #
    ####################################################################################
    def print_table(self):
        # Clear the console
        if self.clear_console:
            os.system("cls")

        [bext.show if self.show_cursor else bext.hide][0]()

        # Print table title if any
        if self.table_title:
            if self.table_title_top_border:
                print(self.table_title_top_border * self.table_width)

            tt = self.table_title
            tt = tt.upper() if self.table_title_caps else tt
            tt = tt.center(self.table_width) if self.table_title_centered else tt
            print(tt)

        # Print headers if any
        if self.headers:
            if self.headers_top_border:
                print(self.headers_top_border * self.table_width)

            if self.headers_upper:
                self.headers = [h.upper() for h in self.headers]

            self.headers = [
                header.center(self.column_widths[index])
                if self.headers_centered
                else header.ljust(self.column_widths[index])
                for index, header in enumerate(self.headers)
            ]
            print(f' {" | ".join(self.headers)} ')

            border_line = [f"{'-' * value}" for value in self.column_widths.values()]
            border_line = "-+-".join(border_line)
            print(f"-{border_line}-")

        # Print rows top border if any
        if self.rows_top_border:
            print(self.rows_top_border * self.table_width)

        # Print rows, highlighting them if necessary
        self.visible_rows = self.get_visible_rows()
        for x, row in enumerate(self.visible_rows):
            r_highlight = self.rows_highlight[x] if self.rows_highlight else None
            line = []
            for y, cell in enumerate(row):
                target_width = self.column_widths[y]
                cell = cell.center(target_width) if self.rows_centered else cell
                highlighted = f"{WHITE}{cell}{END_HIGHLIGHT}"
                data = highlighted if [x, y] == self.highlight else cell
                if self.rows_highlight:
                    data = f"{r_highlight}{cell}{END_HIGHLIGHT}"
                line.append(data)
            wall = f"{r_highlight} | {END_HIGHLIGHT}" if self.rows_highlight else " | "
            line = wall.join(line)
            print(f" {line} ")

        # Print rows bottom border if any
        if self.rows_bottom_border:
            print(self.rows_bottom_border * self.table_width)

        # Print footer if any
        if self.footer:
            for action in self.footer:
                line = action.name
                line = line.center(self.table_width) if self.footer_centered else line
                print(line)

        # Print pagination is needed
        if self.has_multiple_pages:
            arrow_l = "        " if self.current_page == 1 else "[Z] <<< "
            arrow_r = "        " if self.current_page == self.max_page else " >>> [X]"

            pag = f"{arrow_l}[{self.current_page:02}/{self.max_page:02}]{arrow_r}"
            pag = pag.center(self.table_width)

            print(pag)

    ####################################################################################
    #    TABLE CALCULATIONS                                                            #
    ####################################################################################
    @staticmethod
    def get_rows(rows):
        rows = [""] if not rows else rows
        rows = [rows] if not isinstance(rows, list) else rows
        result = [[r] if not isinstance(r, list) else r for r in rows]

        result = [["Nothing to show"]] if not result else result

        return result

    def get_max_rows(self, max_rows):
        result = max_rows if max_rows else len(self.rows)

        return result

    def get_max_columns(self, max_columns=None):
        result = max_columns if max_columns else max([len(r) for r in self.rows])

        return result

    def get_table_width(self, expected_width):
        if expected_width:
            return expected_width

        # TODO If no expected width
        known_lengths = []

        # Calculate the widest possible title length
        title_width = len(self.table_title) + self.side_padding_length
        known_lengths.append(title_width)

        # Calculate the widest possible row length
        max_row = max([sum([len(e) for e in row]) for row in self.visible_rows])
        max_row_length = max_row + self.walls_length + self.side_padding_length
        known_lengths.append(max_row_length)

        table_width = max(known_lengths)

        return table_width

    def get_column_widths(self, widths_types=None):
        # === Variables ================================================================
        taken = self.walls_length + self.side_padding_length
        rows = self.visible_rows

        # === Get max content length for rows ==========================================
        widths_max = {i: max([len(r[i]) for r in rows]) for i in range(len(rows[0]))}

        # === Adjust it if there are headers ===========================================
        if self.headers:
            widths_headers = {i: len(head) for i, head in enumerate(self.headers)}
            lists = widths_max.values(), widths_headers.values()
            adjusted = {i: max(row, head) for i, (row, head) in enumerate(zip(*lists))}
            widths_max = adjusted

        # === Get widths types if none were specified ==================================
        if not widths_types or len(widths_types) > self.max_columns:
            widths_types = {i: ColumnWidth.FULL for i in range(self.max_columns)}

        # === Make column width fit table width by adding spaces =======================
        length_available = self.table_width - (sum(widths_max.values()) + taken)
        full = [k for k, v in widths_types.items() if v == ColumnWidth.FULL]

        if not full:
            far_right_column = list(widths_max.keys())[-1]
            widths_max[far_right_column] += length_available
            length_available = 0

        if length_available < 0:
            raise Exception(
                f"\n[ERROR] Something is wrong!\n"
                f"{length_available = }\n"
                f"{self.table_width = }\n"
                f"{(sum(widths_max.values()) + taken) = }\n"
                f"{sum(widths_max.values()) = }\n"
                f"{taken = }\n"
                f"{widths_max = }\n"
            )

        while length_available:
            smallest = min([v for k, v in widths_max.items() if k in full])
            indices = [k for k, v in widths_max.items() if v == smallest and k in full]
            for index in indices:
                if length_available and index in full:
                    widths_max[index] += 1
                    length_available -= 1

        return widths_max

    def get_visible_rows(self):
        previous_page = self.current_page - 1
        start = self.max_rows * previous_page
        end = self.max_rows * self.current_page

        pack = self.rows[start:end]

        if len(pack) != self.max_rows:
            diff = self.max_rows - len(pack)
            for _ in range(diff):
                dummy = ["" for __ in range(self.max_columns)]
                pack.append(dummy)

        return pack

    def get_cage(self):
        x_axis = [number for number in range(self.max_rows)]
        y_axis = [number for number in range(self.max_columns)]

        coordinates = []
        for x in x_axis:
            for y in y_axis:
                coordinates.append([x, y])

        return coordinates

    def get_max_page(self):
        if self.has_multiple_pages:
            max_page = ceil(len(self.rows) / self.max_rows)

            return max_page

    def get_multiple_pages(self):
        is_multiple_pages = bool(len(self.rows) > self.max_rows)

        return is_multiple_pages

    def get_walls_length(self):
        result = (self.max_columns - 1) * self.wall_length

        return result

    def set_nothing_to_show_state(self):
        self.rows = [["Nothing to show"]]
        self.max_columns = 1
        self.walls_length = self.get_walls_length()
        self.column_widths = self.get_column_widths()

from Code.AlbumEntry import NEW, CHECKED
from Code.constants import DATABASE, ERROR_START, ERROR_END

STATUS_TRANSITION = {NEW: CHECKED, CHECKED: NEW}


def change_album_status(main, album):
    change_value_on_backend(album)
    change_value_on_frontend(main, album)


def change_value_on_backend(album):
    df = DATABASE.read_table()

    album_entry = df.loc[df.URL == album.url]
    assert len(album_entry) == 1, "Found too many albums"
    target_db_index = album_entry.index.values[0]

    current_status = df.loc[target_db_index, "Status"]
    new_status = STATUS_TRANSITION[current_status]
    df.loc[target_db_index, "Status"] = new_status

    DATABASE.write_to_table(df)


def change_value_on_frontend(main, album):
    target_album = f"[{album.year}] {album.title}"
    indices = [i for i, r in enumerate(main.table.rows) if r[0].strip() == target_album]
    assert len(indices) == 1, (
        f"{ERROR_START}\n"
        f"Found too many indices\n"
        f"{album.title = }\n"
        f"{main.table.rows = }\n"
        f"{indices = }\n"
        f"{ERROR_END}"
    )
    target_index = indices[0]

    current_status = main.table.rows[target_index][1]
    new_status = STATUS_TRANSITION[current_status]
    main.table.rows[target_index][1] = new_status

"""Module used for database migration."""
import shutil
import os.path as pt
import monospace

try:
    from android.storage import app_storage_path
except ImportError:
    pass


CURRENT_DB_NAME = 'current.db'
CURRENT_DB_RES = 'current'
main_db_path = None

APP_DB_PATH = app_storage_path() if monospace.on_android else None

MAIN_DB_VERSION = 3      # PRAGMA user_version

GET_VER_QUERY = 'PRAGMA user_version'
SET_VER_QUERY = 'PRAGMA user_version=?'


def upgrade_db(cur_db):
    """Apply all the upgrades to the current db to match the main."""
    cursor = cur_db.cursor()
    cursor.execute(GET_VER_QUERY)
    cur_version = next(cursor)[0]

    for ver in range(cur_version, MAIN_DB_VERSION):
        upgrade_fun = VERSION_UPGRADES.get(ver + 1)

        # If no upgrade function is found, simply dump a new db from main
        if upgrade_fun is None:
            print('Migration error, falling back')
            dump_main_db(True)
        else:
            print('Migrating to ver', ver + 1)
            upgrade_fun(cur_db)
            # Update version
            cursor = cur_db.cursor()
            # Can't use ? parameter with pragma..?
            cursor.execute(SET_VER_QUERY.replace('?', str(ver + 1)))
            cur_db.commit()


def dump_main_db(overwrite=False):
    """Dump a copy of the main db as current."""
    if monospace.on_android:
        new_db_filename = pt.join(APP_DB_PATH, CURRENT_DB_NAME)
    else:
        db_dirname = pt.dirname(main_db_path)
        new_db_filename = pt.join(db_dirname, CURRENT_DB_NAME)

    if not pt.isfile(new_db_filename) or overwrite:
        if overwrite:
            print('Overwriting current db')
        else:
            print('Current db not found, instantiating')
        shutil.copy2(main_db_path, new_db_filename)

    return new_db_filename


def add_movement_ratio(db):
    """Apply a patch and add the 'movement_ratio' option."""
    cursor = db.cursor()
    cursor.execute("INSERT INTO `options`(`option_name`, `value`) "
                   + "VALUES('movement_ratio', 0)")
    db.commit()


def add_ships_and_events(db):
    """Apply a patch and add the needed tables for multiship management.

    Also add a setting(the currently selected ship) and the halloween event
    along with an halloween event ship.
    """
    cursor = db.cursor()

    # New tables
    cursor.execute(
        "CREATE TABLE `events`(`id` INTEGER PRIMARY KEY AUTOINCREMENT,"
        "`name` TEXT, `from_month` INTEGER, `from_day` INTEGER,"
        "`to_month` INTEGER, `to_day` INTEGER)")

    cursor.execute(
        "CREATE TABLE `ships`(`name` TEXT PRIMARY KEY,"
        "`unlocked` INTEGER)")

    cursor.execute(
        "CREATE TABLE `event_ships`("
        "`ship_name` TEXT,"
        "`event_id` INTEGER,"
        "PRIMARY KEY (`ship_name`, `event_id`),"
        "FOREIGN KEY (`ship_name`) REFERENCES `ships`(`name`),"
        "FOREIGN KEY (`event_id`) REFERENCES `events`(`id`))")

    cursor.execute(
        "CREATE TABLE `point_ships`("
        "`ship_name` TEXT PRIMARY KEY,"
        "`total_points` INTEGER,"
        "FOREIGN KEY (`ship_name`) REFERENCES `ships`(`name`))")

    # New option (selected_ship)
    cursor.execute("INSERT INTO `options`(`option_name`, `value`) "
                   "VALUES('selected_ship', 'default')")

    # Halloween event
    cursor.execute(
        "INSERT INTO events(name, from_month, from_day, to_month, to_day) "
        "VALUES('halloween', 10, 21, 11, 10)")

    # Halloween ship
    cursor.execute(
        "INSERT INTO `ships`(`name`, `unlocked`) VALUES('halloween_ship', 0)")

    cursor.execute(
        "INSERT INTO `event_ships`(`ship_name`, `event_id`) "
        "VALUES('halloween_ship', 1)")

    db.commit()


def add_username(db):
    """Add 'username' column to the options table.

    Also add a 'username_added' to manage initial setup.
    """
    cursor = db.cursor()

    cursor.execute("INSERT INTO `options`(`option_name`, `value`) "
                   "VALUES('username', 'AAA')")
    cursor.execute("INSERT INTO `options`(`option_name`, `value`) "
                   "VALUES('username_added', 0)")

    db.commit()


VERSION_UPGRADES = {
    1: add_movement_ratio,
    2: add_ships_and_events,
    3: add_username
}

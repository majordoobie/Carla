import sqlite3


class BotDatabase:
    def __init__(self, db_filepath):
        self.conn = None
        self.cursor = None
        if db_filepath:
            self.open_db(db_filepath)

    def open_db(self, db_filepath):
        """Open database, create if need be and set foreign_keys to on"""
        try:
            self.conn = sqlite3.connect(db_filepath)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = 1")  # Enables foreign keys
            self.instantiate_db()
        except sqlite3.Error as e:
            print(f"Unable to connect to {db_filepath}\n{e}")

    def close_db(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def instantiate_db(self):
        """Method creates the database if they do not exist"""
        create_helpers_table = ('''\
        CREATE TABLE IF NOT EXISTS helpers (
            discord_id INT NOT NULL,
            discord_name TEXT NOT NULL,
            PRIMARY KEY(discord_id)
        )
        ''')
        create_mapping_table = ('''\
        CREATE TABLE IF NOT EXISTS archive_mapping (
            channel_id INT NOT NULL,
            channel_name TEXT NOT NULL,
            PRIMARY KEY(channel_id)
        )
        ''')
        create_role_sync_table = ('''\
        CREATE TABLE IF NOT EXISTS role_sync (
            role_id INT NOT NULL,
            role_name TEXT NOT NULL,
            PRIMARY KEY(role_id)
        )''')

        self.cursor.execute(create_helpers_table)
        self.cursor.execute(create_mapping_table)
        self.cursor.execute(create_role_sync_table)
        self.conn.commit()

    def fetch_table(self, table):
        sql = f'SELECT * FROM {table}'
        self.cursor.execute(sql)
        return self.cursor.fetchall()

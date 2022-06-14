import os
from typing import List
from dotenv import load_dotenv
import mysql.connector as database

# Load data from .env file
load_dotenv()


class SqlHelper:
    def __init__(self, db_name):
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.db_con = database.connect(
            user=self.username,
            password=self.password,
            host=self.host,
            database=f"{db_name}",
        )
        self.db_cur = self.db_con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, e_type, e_val, e_trc):
        self.close()

    @property
    def connection(self):
        return self.db_con

    @property
    def cursor(self):
        return self.db_cur

    def commit(self):
        self.db_con.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def get_guild_channel_id(self, guild_id):
        if self.guild_exists(guild_id):
            sql = "SELECT member_count_channel_id FROM guilds WHERE guild_id=%s"
            self.execute(sql, (guild_id,))
            return self.fetchone()[0]
        return None

    def get_prefix(self, guild_id):
        if self.guild_exists(guild_id):
            sql = "SELECT prefix FROM guilds WHERE guild_id=%s"
            self.execute(sql, (guild_id,))
            return self.fetchone()[0]
        return None

    def set_prefix(self, guild_id, new_prefix) -> bool:
        if self.guild_exists(guild_id):
            sql = "UPDATE guilds SET prefix=%s WHERE guild_id=%s"
            self.execute(
                sql,
                (
                    new_prefix,
                    guild_id,
                ),
            )
            self.commit()
            return True
        return False

    def guild_exists(self, guild_id):
        sql = "SELECT guild_id FROM guilds WHERE guild_id=%s"
        if len(self.query(sql, (guild_id,))) > 0:
            return True
        return False

    def add_guild(self, guild_name, guild_id):
        if self.guild_exists(guild_id):
            return False
        self.execute(
            "INSERT INTO guilds (guild_name, guild_id) VALUES (%s,%s)",
            (
                guild_name,
                guild_id,
            ),
        )
        self.commit()
        return True

    # Clean up orphaned guild entries in the database that occur when someone removes the bot from a guild while it's offline
    def check_guilds_remove(self, guild_list: List):
        self.execute("SELECT guild_id FROM guilds")
        guilds_in_db = self.fetchall()

        # Using a set to avoid O(n) lookup for deletion continually in for loop
        guild_ids = [guilds[0] for guilds in guilds_in_db]
        guilds_dict = set(guild_ids)

        # Delete any guilds in the database that the bot isn't apart of
        for guild in guild_list:
            guilds_dict.remove(guild.id)
        for guild_rmv in guilds_dict:
            self.execute("DELETE FROM guilds WHERE guild_id=%s", (guild_rmv,))

    def delete_guild(self, guild_id):
        if self.guild_exists(guild_id):
            self.execute("DELETE FROM guilds WHERE guild_id=%s", (guild_id,))
            self.commit()
            return True
        return False

    def update_guild_channel_id(self, guild_id, channel_id):
        if self.guild_exists(guild_id):
            sql = "UPDATE guilds SET member_count_channel_id=%s WHERE guild_id=%s"
            self.execute(
                sql,
                (
                    channel_id,
                    guild_id,
                ),
            )
            self.commit()
            return True
        return False

    def update_guild_name(self, guild_name, guild_id):
        if self.guild_exists(guild_id):
            self.execute(
                "UPDATE guilds SET guild_name=%s WHERE guild_id=%s",
                (
                    guild_name,
                    guild_id,
                ),
            )
            self.commit()
            return True
        return False

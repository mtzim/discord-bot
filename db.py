import sqlite3


class SqlDatabase:
    def __init__(self, db_name):
        self.db_con = sqlite3.connect(db_name)
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
            sql = "SELECT member_count_channel_id FROM guilds WHERE guild_id=?"
            self.execute(sql, (guild_id,))
            return self.fetchone()[0]
        return None

    def guild_exists(self, guild_id):
        sql = "SELECT guild_id FROM guilds WHERE guild_id=?"
        if len(self.query(sql, (guild_id,))) > 0:
            return True
        return False

    def add_guild(self, guild_name, guild_id):
        if self.guild_exists(guild_id):
            return False
        self.execute(
            "INSERT INTO guilds (guild_name, guild_id) VALUES (?,?)",
            (
                guild_name,
                guild_id,
            ),
        )
        self.commit()
        return True

    def delete_guild(self, guild_id):
        if self.guild_exists(guild_id):
            self.execute("DELETE FROM guilds WHERE guild_id=?", (guild_id,))
            self.commit()
            return True
        return False

    def update_guild_channel_id(self, guild_id, channel_id):
        if self.guild_exists(guild_id):
            sql = "UPDATE guilds SET member_count_channel_id=? WHERE guild_id=?"
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
                "UPDATE guilds SET guild_name=? WHERE guild_id=?",
                (
                    guild_name,
                    guild_id,
                ),
            )
            self.commit()
            return True
        return False

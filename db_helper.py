import os
from typing import List
from dotenv import load_dotenv
import mysql.connector as database

# Load data from .env file
load_dotenv()


class SqlHelper:
    """
    A helper class for SQL database interaction.

    ...

    Attributes
    ----------
    username : str
        A MySQL Database username
    password : str
        A MySQL Database password belonging to the username
    host : str
        The host IP of the MySQL Database
    db_name : str
        The Database name
    db_con : MySQLConnection
        Connection object to the MySQL Database
    db_cur : CursorBase
        Cursor to use for manipulating database information

    Methods
    -------
    connection()
        Managed connection attribute
    cursor()
        Managed cursor attribute
    commit()
        Commits changes to the database
    close(commit=True)
        Commits changes to the database before closing the connection
    execute(sql,params=None)
        Execute sql commands
    fetchall()
        Performs a fetchall on the database
    fetchone()
        Performs a fetchone on the databse
    query(sql,params=None)
        Query the database and fetch the results
    get_guild_channel_id(guild_id)
        Retrieve a guild's channel id from the database
    get_prefix(guild_id)
        Retrieve a guild's prefix from the database
    set_prefix(guild_id,new_prefix)
        Set a guild's prefix in the database with the new prefix
    guild_exists(guild_id)
        Check if a guild exists within the database
    add_guild(guild_name,guild_id)
        Adds a guild to the database
    check_guilds_remove(guild_list)
        Check if the database is synced with a guild_list and remove guilds that aren't on the guild_list
    delete_guild(guild_id)
        Remove a guild from the database
    update_guild_channel_id(guild_id,channel_id)
        Update a guild's channel id that controls member count in the database
    update_guild_name(guild_name,guild_id)
        Update a guild's name in the database
    """

    def __init__(self):
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.db_name = os.getenv("DB_NAME")
        self.db_con = database.connect(
            user=self.username,
            password=self.password,
            host=self.host,
            database=self.db_name,
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
        """
        Retrieve a guild's channel id from the database

        ...

        Parameters
        ----------
        guild_id : int
            A guild's id

        Returns
        -------
        int, None
            The guild's id if it was found in the database
        """
        if self.guild_exists(guild_id):
            sql = "SELECT member_count_channel_id FROM guilds WHERE guild_id=%s"
            self.execute(sql, (guild_id,))
            return self.fetchone()[0]
        return None

    def get_prefix(self, guild_id):
        """
        Retrieve a guild's prefix from the database

        ...

        Parameters
        ----------
        guild_id : int
            A guild's id

        Returns
        -------
        str
            The guild's prefix if it was found in the database
        """
        if self.guild_exists(guild_id):
            sql = "SELECT prefix FROM guilds WHERE guild_id=%s"
            self.execute(sql, (guild_id,))
            return self.fetchone()[0]
        return None

    def set_prefix(self, guild_id, new_prefix) -> bool:
        """
        Set a guild's prefix in the database with the new prefix

        ...

        Parameters
        ----------
        guild_id : int
            A guild's id
        new_prefix : str
            A guild's new prefix

        Returns
        -------
        bool
            Whether or not updating the prefix was successful or not
        """
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
        """
        Adds a guild to the database

        ...

        Parameters
        ----------
        guild_name : str
            A guild's name
        guild_id : int
            A guild's id

        Returns
        -------
        bool
            Whether or not adding the guild to the database was successful or not
        """
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
        """
        Check if the database is synced with a guild_list and remove guilds that aren't on the guild_list

        ...

        Parameters
        ----------
        guild_list : List
            A list of guilds that a discord bot is a member of
        """
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
        """
        Remove a guild from the database

        ...

        Parameters
        ----------
        guild_id : int
            A guild's id

        Returns
        -------
        bool
            Whether or not removing the guild from the database was successful or not
        """
        if self.guild_exists(guild_id):
            self.execute("DELETE FROM guilds WHERE guild_id=%s", (guild_id,))
            self.commit()
            return True
        return False

    def update_guild_channel_id(self, guild_id, channel_id):
        """
        Update a guild's channel id that controls member count in the database

        ...

        Parameters
        ----------
        guild_id : int
            A guild's id
        channel_id : int
            A guild channel's id

        Returns
        -------
        bool
            Whether or not updating the guild's channel id in the database was successful or not
        """
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
        """
        Update a guild's name in the database

        ...

        Parameters
        ----------
        guild_name : str
            A guild's name
        guild_id : int
            A guild's id

        Returns
        -------
        bool
            Whether or not updating the guild's name in the database was successful or not
        """
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

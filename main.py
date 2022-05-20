import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands


def setup_logging():
    # Create logging directory
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    # Setup logging
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        filename="./logs/discord.log", encoding="utf-8", mode="w"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)


def main():
    setup_logging()
    load_dotenv()

    # enable necessary Gateway features
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    bot = commands.Bot(command_prefix="?", description="Nothing yet", intents=intents)

    # called when the client is done preparing the data received from Discord
    @bot.event
    async def on_ready():
        print(f"Logged into Discord as {bot.user} (ID: {bot.user.id})")

        # list all guilds bot is connected to
        if len(bot.guilds) > 0:
            print("Connected to the following guilds:")

            for count, guild in enumerate(bot.guilds):
                print(
                    f"{count+1}) {guild.name}#{guild.id} - Members: {len(guild.members)}"
                )
                await update_channel_member_count(guild)

    # called when a new member joins a guild
    @bot.event
    async def on_member_join(member):
        print(f"{member} joined {member.guild}.")
        await update_channel_member_count(member.guild)

    # called when a member leaves or gets removed from a guild
    @bot.event
    async def on_member_remove(member):
        print(f"{member} left {member.guild}.")
        await update_channel_member_count(member.guild)

    # if the guild has a member count channel, update it
    async def update_channel_member_count(guild):
        channel_id = get_channel_id_member_count(guild)
        if channel_id != None:
            channel = discord.utils.get(guild.channels, id=channel_id)
            channel_name = f"Members - {len(guild.members)}"

            await channel.edit(name=channel_name)
        else:
            print(f"channel id not found, can't update member count for {guild}")

    # return guild's channel id to edit if guild has a designated channel to edit
    def get_channel_id_member_count(guild):
        channel_id = os.getenv("GUILD_CHANNEL")
        guild_id = os.getenv("GUILD_ID")

        if int(guild_id) == guild.id:
            return int(channel_id)

        return None

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()

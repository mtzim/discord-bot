import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command, Group
from typing import Any, List, Mapping, Optional


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self, **options: Any) -> None:
        super().__init__(**options)

    async def send_bot_help(
        self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]], /
    ) -> None:
        description = """**<:botAvatar:978780970377433178> Hello! I'm Mybot!**\n
        Below you can see all the commands I know.
        If you have any questions or comments about something ask on [Github](https://github.com/mtzim/discord-bot).\n
        **Have a nice day!**"""
        color = discord.Color.blue()
        to_embed = discord.Embed(description=description, color=color)
        return await self.get_destination().send(embed=to_embed)

    async def send_cog_help(self, cog: Cog, /) -> None:
        return await super().send_cog_help(cog)

    async def send_group_help(self, group: Group[Any, ..., Any], /) -> None:
        return await super().send_group_help(group)

    async def send_command_help(self, command: Command[Any, ..., Any], /) -> None:
        return await super().send_command_help(command)

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

        trailing_text = """\n\n**Use `?help <Category>` for more information about a category.**
        **Use `?help <Command>` for more information about a command.**\n
        **Examples:**
        `?help Shutdown` for an overview of the Shutdown category.
        `?help set_channel` for detailed help for the set_channel command.\n
        **Useful links:**
        [Github](https://github.com/mtzim/discord-bot)"""

        color = discord.Color.blue()
        to_embed = discord.Embed(description=description, color=color)

        to_embed = to_embed.add_field(name="GuildMemberCount", value=f"`set_channel`")
        to_embed = to_embed.add_field(
            name="Shutdown", value=f"`shutdown`", inline=False
        )

        # \u2800 is an invisible unicode character
        to_embed = to_embed.add_field(
            name="\u2800", value=f"{trailing_text}", inline=False
        )

        return await self.get_destination().send(embed=to_embed)

    async def send_cog_help(self, cog: Cog, /) -> None:
        return await super().send_cog_help(cog)

    async def send_group_help(self, group: Group[Any, ..., Any], /) -> None:
        return await super().send_group_help(group)

    async def send_command_help(self, command: Command[Any, ..., Any], /) -> None:
        return await super().send_command_help(command)

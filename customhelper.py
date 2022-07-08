import itertools
import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command, Group
from typing import Any, List, Mapping, Optional, Sequence


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self, **options: Any) -> None:
        self.no_category: str = options.pop("no_category", "MyBot")
        self.sort_commands: bool = options.pop("sort_commands", True)
        options["command_attrs"] = {"help": "Usage: `?help <Command>`"}
        super().__init__(**options)

        self.help_msg = discord.Embed(color=discord.Color.blue())

    def add_field(self, name, value, inline: Optional[bool] = False):
        """Adds a Cog/Category with all commands related to it to the help message."""
        self.help_msg = self.help_msg.add_field(name=name, value=value, inline=inline)

    def add_ending(self):
        trailing_text = """\n\n**Use `?help <Command>` for more information about a command.**\n
        **Examples:**
        `?help set_channel` for detailed help for the set_channel command.\n
        **Useful links:**
        [Github](https://github.com/mtzim/discord-bot)"""

        # \u2800 is an invisible unicode character, can also maybe use \u200b
        self.add_field("\u2800", f"{trailing_text}", inline=False)

    def add_section(
        self, commands: Sequence[commands.Command[Any, ..., Any]], /, *, heading: str
    ):
        """Joins multiple commands from a Cog/Category together in a comma seperated string
        to pass as a single value into add_field since it only takes one value in relation
        to its name"""
        if not commands:
            return

        command_list = []
        for command in commands:
            name = command.name
            entry = f"{name}"
            command_list.append(f"`{entry}`")
        value = "**,** ".join(command_list)
        self.add_field(name=heading, value=value)

    async def send_bot_help(
        self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]], /
    ) -> None:

        ctx = self.context
        bot = ctx.bot

        self.help_msg.set_author(
            name=f"Hello! I'm {bot.user.name}!",
            icon_url=f"{bot.user.display_avatar.url}",
        )
        # self.help_msg.set_thumbnail(url=f"{bot.user.display_avatar.url}")

        description = f"""Below you can see all the commands I know.
        If you have any questions or comments about something ask on [Github](https://github.com/mtzim/discord-bot).\n
        **Have a nice day!**"""

        self.help_msg.description = description

        def get_category(command, *, no_category=self.no_category):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        # Now we can add the commands to the page.
        for category, commands in to_iterate:
            commands = (
                sorted(commands, key=lambda c: c.name)
                if self.sort_commands
                else list(commands)
            )
            self.add_section(commands, heading=category)

        self.add_ending()

        return await self.get_destination().send(embed=self.help_msg)

    def command_not_found(self, string: str, /) -> str:
        self_category = self.no_category
        return f"No command called `{string}` found."

    # Treat cog help as a command when user uses `help CogName`
    async def send_cog_help(self, cog: Cog, /) -> None:
        ignore_cogs = f"No command called `{cog.qualified_name}` found."
        return await self.get_destination().send(content=ignore_cogs)

    async def send_group_help(self, group: Group[Any, ..., Any], /) -> None:
        return await super().send_group_help(group)

    async def send_command_help(self, command: Command[Any, ..., Any], /) -> None:
        ctx = self.context

        signature = self.get_command_signature(command)
        if command.help:
            usage = f"{command.help.replace(f'?{command}',f'{ctx.prefix}{command}')}"
        else:
            usage = f"Usage: `{signature}`"

        return await self.get_destination().send(content=usage)

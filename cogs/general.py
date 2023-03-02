import discord
from discord.ext import commands
from discord.ui import Button, Select, View
from discord import ButtonStyle
from discord import app_commands
from typing import Dict, Optional


class NavigationView(View):
    @discord.ui.button(emoji="⏮️", disabled=True, custom_id="start")
    async def btn_start_callback(
        self, interaction: discord.Interaction, button: Button
    ):
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="◀️", disabled=True, custom_id="back")
    async def btn_back_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Button clicked!")

    @discord.ui.button(emoji="▶️", custom_id="forward")
    async def btn_forward_callback(
        self, interaction: discord.Interaction, button: Button
    ):
        button1 = [x for x in self.children if x.custom_id == "start"][0]
        button2 = [x for x in self.children if x.custom_id == "back"][0]
        button1.disabled = False
        button2.disabled = False
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="⏭️", custom_id="end")
    async def btn_end_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Button clicked!")

    @discord.ui.button(style=ButtonStyle.danger, emoji="✖️", custom_id="danger")
    async def btn_stop_callback(self, interaction: discord.Interaction, button: Button):
        msg = interaction.message.content
        await interaction.response.edit_message(content=msg, view=None)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: General loaded.")

    # /help
    # /help command
    # /help command subcommand
    # /help command option
    # /help category
    # check if category - output category info (how to retrieve category/module)
    # check if command - output command info (how to retrieve command specific info)
    # if not a command or category - error (how to catch errors in slash commands/this case)
    # get command description in main.py and add bot name there?
    @app_commands.command(
        name="help",
        description=f"Learn about commands and supported features",
        extras={"module": "General"},
    )
    @app_commands.describe(input="[STRING] Category, Command, or Page")
    async def slash_help(
        self, interaction: discord.Interaction, input: Optional[str]
    ) -> None:
        # self.bot.help_dict.keys() for all categories
        # self.bot.help_dict.values() for all commands
        slash_commands = [
            command for sub_list in self.bot.help_dict.values() for command in sub_list
        ]

        if input is None:
            # help_dict is {'Default': ['hello', 'help']}
            bot_name = interaction.client.application.name
            avatar_url = interaction.client.application.icon.url
            description = f"""Below you can see all the commands I know.
            If you have any questions or comments about something ask on [Github](https://github.com/mtzim/discord-bot).\n
            **Have a nice day!**"""
            trailing_text = """\n\n`help commandName` - Command Details
            `help commandName subCommandName` - Sub Command Details
            `help commandName optionName` - Option Details
            `help categoryName` - Category Details"""
            embedMsg = discord.Embed(color=discord.Color.blue())
            embedMsg.set_author(
                name=f"Hello! I'm {bot_name}!", icon_url=f"{avatar_url}"
            )
            embedMsg.set_thumbnail(url=avatar_url)
            embedMsg.description = description
            # Sort dictionary category names alphabetically
            sorted_help = dict(sorted(self.bot.help_dict.items()))
            command_list = []
            for key in sorted_help.keys():
                for command in sorted_help[key]:
                    command_list.append(f"`{command}`")
                value = ", ".join(command_list)
                embedMsg.add_field(name=key, value=value, inline=False)
                command_list.clear()
            # \u2800 is an invisible unicode character, can also maybe use \u200b
            embedMsg.add_field(name="\u2800", value=f"{trailing_text}", inline=False)
            await interaction.response.send_message(embed=embedMsg)
        elif input in slash_commands:
            cmd_info = self.bot.tree.get_command(input)
            desc = cmd_info.description
            params = cmd_info.parameters
            option_txt = "```"
            for count, param in enumerate(params, start=1):
                split_desc = param.description.split("]")
                option_txt = f"{option_txt}{count} : {param.name}{split_desc[0]}] -{split_desc[1]}\n"
            option_txt = f"{option_txt}```"

            help_cmd_msg = (
                f"**Command**: `{input}`\n**Description**: {desc}\n\n**Options**:\n"
            )

            help_cmd_msg = help_cmd_msg + option_txt
            view = NavigationView()
            await interaction.response.send_message(content=help_cmd_msg, view=view)


async def setup(bot):
    await bot.add_cog(General(bot))

import discord
from discord.ext import commands
from discord.ui import Button, Select, View
from discord import ButtonStyle
from discord import app_commands
from typing import Dict, List, Optional


class NavigationView(View):
    def __init__(
        self,
        cmd_info: Optional[app_commands.Command] = None,
        option_data: Optional[List[str]] = None,
    ):
        super().__init__()
        self.option_data = option_data
        self.cmd_info = cmd_info

        desc = self.cmd_info.description
        params = self.cmd_info.parameters
        self.help_cmd_intro = (
            f"**Command**: `{cmd_info.name}`\n**Description**: {desc}\n\n**Options**:\n"
        )

        if self.option_data != None:
            self.pages = len(self.option_data)
            self.curr_page = 1

        # self.help_cmd_msg = f"{self.help_cmd_intro}```Page {self.curr_page}/{self.pages}\n{self.option_data[self.curr_page-1]}```"

    @discord.ui.button(emoji="⏮️", disabled=True, custom_id="start")
    async def btn_start_callback(
        self, interaction: discord.Interaction, button: Button
    ):
        button_start = [x for x in self.children if x.custom_id == "start"][0]
        button_back = [x for x in self.children if x.custom_id == "back"][0]
        button_forward = [x for x in self.children if x.custom_id == "forward"][0]
        button_end = [x for x in self.children if x.custom_id == "end"][0]
        button_start.disabled = True
        button_back.disabled = True
        button_forward.disabled = False
        button_end.disabled = False

        self.curr_page = 1

        select = [x for x in self.children if x.custom_id == "select_options"][0]
        self.remove_item(select)
        self.add_item(
            SelectOption(
                cmd_info=self.cmd_info, option_data=self.option_data[self.curr_page - 1]
            )
        )

        help_cmd_msg = f"{self.help_cmd_intro}```Page {self.curr_page}/{self.pages}\n{self.option_data[self.curr_page-1]}```"
        await interaction.response.edit_message(content=help_cmd_msg, view=self)

    @discord.ui.button(emoji="◀️", disabled=True, custom_id="back")
    async def btn_back_callback(self, interaction: discord.Interaction, button: Button):

        self.curr_page -= 1

        if self.curr_page == 1:
            button_start = [x for x in self.children if x.custom_id == "start"][0]
            button_back = [x for x in self.children if x.custom_id == "back"][0]
            button_start.disabled = True
            button_back.disabled = True

        select = [x for x in self.children if x.custom_id == "select_options"][0]
        self.remove_item(select)
        self.add_item(
            SelectOption(
                cmd_info=self.cmd_info, option_data=self.option_data[self.curr_page - 1]
            )
        )

        help_cmd_msg = f"{self.help_cmd_intro}```Page {self.curr_page}/{self.pages}\n{self.option_data[self.curr_page-1]}```"
        await interaction.response.edit_message(content=help_cmd_msg, view=self)

    @discord.ui.button(emoji="▶️", custom_id="forward")
    async def btn_forward_callback(
        self, interaction: discord.Interaction, button: Button
    ):
        button_start = [x for x in self.children if x.custom_id == "start"][0]
        button_back = [x for x in self.children if x.custom_id == "back"][0]
        button_start.disabled = False
        button_back.disabled = False

        self.curr_page += 1

        if self.curr_page == self.pages:
            button_forward = [x for x in self.children if x.custom_id == "forward"][0]
            button_end = [x for x in self.children if x.custom_id == "end"][0]
            button_forward.disabled = True
            button_end.disabled = True

        select = [x for x in self.children if x.custom_id == "select_options"][0]
        self.remove_item(select)
        self.add_item(
            SelectOption(
                cmd_info=self.cmd_info, option_data=self.option_data[self.curr_page - 1]
            )
        )

        help_cmd_msg = f"{self.help_cmd_intro}```Page {self.curr_page}/{self.pages}\n{self.option_data[self.curr_page-1]}```"
        await interaction.response.edit_message(content=help_cmd_msg, view=self)

    @discord.ui.button(emoji="⏭️", custom_id="end")
    async def btn_end_callback(self, interaction: discord.Interaction, button: Button):
        button_start = [x for x in self.children if x.custom_id == "start"][0]
        button_back = [x for x in self.children if x.custom_id == "back"][0]
        button_forward = [x for x in self.children if x.custom_id == "forward"][0]
        button_end = [x for x in self.children if x.custom_id == "end"][0]
        button_start.disabled = False
        button_back.disabled = False
        button_forward.disabled = True
        button_end.disabled = True

        self.curr_page = self.pages

        select = [x for x in self.children if x.custom_id == "select_options"][0]
        self.remove_item(select)
        self.add_item(
            SelectOption(
                cmd_info=self.cmd_info, option_data=self.option_data[self.curr_page - 1]
            )
        )

        help_cmd_msg = f"{self.help_cmd_intro}```Page {self.curr_page}/{self.pages}\n{self.option_data[self.curr_page-1]}```"
        await interaction.response.edit_message(content=help_cmd_msg, view=self)

    @discord.ui.button(style=ButtonStyle.danger, emoji="✖️", custom_id="danger")
    async def btn_stop_callback(self, interaction: discord.Interaction, button: Button):
        msg = interaction.message.content
        await interaction.response.edit_message(content=msg, view=None)


class SingleView(View):
    def __init__(
        self,
        cmd_info: Optional[app_commands.Command] = None,
        option_data: Optional[str] = None,
    ):
        self.cmd_info = cmd_info
        self.option_data = option_data
        super().__init__()

    @discord.ui.button(style=ButtonStyle.success, label="Choose", custom_id="choose")
    async def btn_choose_callback(
        self, interaction: discord.Interaction, button: Button
    ):
        parse_selection = self.option_data.split("-")[0].split(":")[1].split("[")
        opt = parse_selection[0].strip()
        opt_type = f"[{parse_selection[1]}"
        param = self.cmd_info.get_parameter(opt)
        req = param.required
        param_parent = param.command.name
        desc = ""
        fmt_pdesc = param.description.split("]")[1].strip()
        if param.name != fmt_pdesc:
            desc = fmt_pdesc

        param_details = f"**Option**: {opt}\n**Description**: {desc}\n**Type**: {opt_type}\n**Command**: `{param_parent}`\n**Required**: {req}"
        await interaction.response.edit_message(content=param_details, view=None)


class SelectOption(Select):
    def __init__(
        self,
        cmd_info: Optional[app_commands.Command] = None,
        option_data: Optional[str] = None,
    ):

        self.option_data = option_data
        self.cmd_info = cmd_info
        lines = self.option_data.split("\n")
        self.discord_select = []
        for label in lines:
            lab_desc = label.split("-")
            parse_label = lab_desc[0]
            parse_desc = ""
            if len(lab_desc) > 1:
                parse_desc = lab_desc[1]
            fmt_label = parse_label.replace(" :", ":")
            self.discord_select.append(
                discord.SelectOption(label=fmt_label, description=parse_desc)
            )

        super().__init__(
            custom_id="select_options",
            placeholder="Please choose an item",
            options=self.discord_select,
        )

    async def callback(self, interaction):
        # self.values[0] to get the label, format label to remove #: and []
        # search slash commands for details?
        # **Option:** opt (i.e. input)
        # **Description:** desc
        # **Type:** opt_type
        # **Command:** param_parent (i.e. `help`)
        # **Required:** req
        parse_selection = self.values[0].split(":")[1].split("[")
        opt = parse_selection[0].strip()
        opt_type = f"[{parse_selection[1]}"
        param = self.cmd_info.get_parameter(opt)
        req = param.required
        param_parent = param.command.name
        desc = ""
        fmt_pdesc = param.description.split("]")[1].strip()
        if param.name != fmt_pdesc:
            desc = fmt_pdesc

        param_details = f"**Option**: {opt}\n**Description**: {desc}\n**Type**: {opt_type}\n**Command**: `{param_parent}`\n**Required**: {req}"
        await interaction.response.edit_message(content=param_details, view=None)


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: General loaded.")

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

            help_cmd_msg = (
                f"**Command**: `{input}`\n**Description**: {desc}\n\n**Options**:\n"
            )

            # store and retrieve type/desc data in extras for a command instead?
            # find description from param, format description to remove type, compare to param name, if same do nothing
            count = 0
            # option_txt = ""
            page_content = []
            for param in params:
                count += 1
                split_desc = param.description.split("]")
                # print(f"{str(param.type).split('.')[1].upper()}")
                # option_txt = f"{option_txt}{count} : {param.name}{split_desc[0]}] -{split_desc[1]}\n"
                if param.name != split_desc[1].strip():
                    page_content.append(
                        f"{count} : {param.name}{split_desc[0]}] -{split_desc[1]}"
                    )
                else:
                    page_content.append(f"{count} : {param.name}{split_desc[0]}]")
            option_txt = [
                "\n".join(page_content[i : i + 10])
                for i in range(0, len(page_content), 10)
            ]

            pages = len(option_txt)
            # When only 1 option - green choose button
            # when more than 1 option, select menu that is updated by buttons that sync with pages - split up option_txt
            if pages == 1 and count == 1:
                view = SingleView(cmd_info=cmd_info, option_data=option_txt[0])
                help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
                await interaction.response.send_message(content=help_cmd_msg, view=view)
            elif pages == 1 and count <= 10:
                view = View()
                view.add_item(
                    SelectOption(cmd_info=cmd_info, option_data=option_txt[0])
                )
                help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
                await interaction.response.send_message(content=help_cmd_msg, view=view)
            else:
                curr_page = 1
                help_cmd_msg = f"{help_cmd_msg}```Page {curr_page}/{pages}\n{option_txt[curr_page-1]}```"
                view = NavigationView(cmd_info=cmd_info, option_data=option_txt)
                view.add_item(
                    SelectOption(cmd_info=cmd_info, option_data=option_txt[0])
                )
                await interaction.response.send_message(content=help_cmd_msg, view=view)


async def setup(bot):
    await bot.add_cog(General(bot))

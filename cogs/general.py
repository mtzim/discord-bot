import discord
from discord.ext import commands
from discord.ui import Button, Select, View
from discord import ButtonStyle
from discord import app_commands
from typing import Dict, List, Optional
from db_helper import SqlHelper as SQL

# determine if command is a subcommand and get its parent to include full command
def option_details(command_info: app_commands.Command, option: str) -> str:
    """
    Format and return details about a command's parameter.

    Parameters
    ----------
    command_info : app_commands.Command
        The command that the parameter belongs to
    option: str
        The command's parameter that needs parsing

    Returns
    -------
    str
        The formatted details that belong to a command's parameter
    """
    in_group = command_info.parent
    param = command_info.get_parameter(option)
    option_type = f"[{str(param.type).split('.')[1].upper()}]"
    required = param.required
    if not in_group:
        command = param.command.name
    else:
        command = f"{in_group.name} {command_info.name}"
    description = ""
    format_param_desc = param.description.split("]")[1].strip()
    if param.name != format_param_desc:
        description = format_param_desc

    return f"**Option**: {option}\n**Description**: {description}\n**Type**: {option_type}\n**Command**: `{command}`\n**Required**: {required}"


async def group_view_helper(
    cmd_info: app_commands.Group,
    interaction: discord.Interaction,
    bot: commands.Bot,
):
    """
    A group view helper that helps with subcommand handling

    ...

    Parameters
    ----------
    cmd_info : app_commands.Group
        A parent command
    interaction : discord.Interaction
        The interaction caused by a user performing a slash command
    bot : commands.Bot
        A custom Discord Bot
    """
    # subcommands instead of options
    # picking a subcommand here will load its options
    # just like category which also lists commands
    desc = cmd_info.description
    subcommands = cmd_info.commands  # list of subcommands, equiv of list of params

    help_cmd_msg = f"**Command**: `{cmd_info.name}`\n**Description**: {desc}\n\n**Sub Commands**:\n"

    count = 0
    # option_txt = ""
    page_content = []
    for command in subcommands:
        count += 1

        if command.description != "":
            page_content.append(f"{count} : {command.name} - {command.description}")
        else:
            page_content.append(f"{count} : {command.name}")
    option_txt = [
        "\n".join(page_content[i : i + 10]) for i in range(0, len(page_content), 10)
    ]

    pages = len(option_txt)
    # When only 1 option - green choose button
    # when more than 1 option, select menu that is updated by buttons that sync with pages - split up option_txt
    if pages == 1 and count == 1:
        view = SingleButtonView(
            option_data=option_txt[0], is_group=True, group_info=cmd_info, bot=bot
        )
        help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
        await interaction.response.send_message(content=help_cmd_msg, view=view)
    elif pages == 1 and count <= 10:
        view = View()
        view.add_item(
            SelectOption(
                option_data=option_txt[0], is_group=True, group_info=cmd_info, bot=bot
            )
        )
        help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
        await interaction.response.send_message(content=help_cmd_msg, view=view)
    else:
        curr_page = 1
        help_cmd_msg = (
            f"{help_cmd_msg}```Page {curr_page}/{pages}\n{option_txt[curr_page-1]}```"
        )
        view = NavigationView(
            option_data=option_txt, is_group=True, group_info=cmd_info, bot=bot
        )
        view.add_item(
            SelectOption(
                option_data=option_txt[0], is_group=True, group_info=cmd_info, bot=bot
            )
        )
        await interaction.response.send_message(content=help_cmd_msg, view=view)


async def command_view_helper(
    cmd_info: app_commands.Command,
    interaction: discord.Interaction,
    from_categ_view: Optional[bool] = None,
):
    """
    A command view helper that helps with command and parameter handling

    ...

    Parameters
    ----------
    cmd_info : app_commands.Command
        A slash command
    interaction : discord.Interaction
        The interaction caused by a user performing a slash command
    from_categ_view : bool, optional, default=None
        Whether or not this helper is being called from a view or UI item that was handling a category
    """
    desc = cmd_info.description
    params = cmd_info.parameters

    if len(params) > 0:
        in_grp = cmd_info.parent
        if not in_grp:
            help_cmd_msg = f"**Command**: `{cmd_info.name}`\n**Description**: {desc}\n\n**Options**:\n"
        else:
            help_cmd_msg = f"**Command**: `{in_grp.name} {cmd_info.name}`\n**Description**: {desc}\n\n**Options**:\n"
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
            "\n".join(page_content[i : i + 10]) for i in range(0, len(page_content), 10)
        ]

        pages = len(option_txt)
        # When only 1 option - green choose button
        # when more than 1 option, select menu that is updated by buttons that sync with pages - split up option_txt
        if pages == 1 and count == 1:
            view = SingleButtonView(cmd_info=cmd_info, option_data=option_txt[0])
            help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
            if from_categ_view:
                await interaction.response.edit_message(content=help_cmd_msg, view=view)
            else:
                await interaction.response.send_message(content=help_cmd_msg, view=view)
        elif pages == 1 and count <= 10:
            view = View()
            view.add_item(SelectOption(cmd_info=cmd_info, option_data=option_txt[0]))
            help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
            if from_categ_view:
                await interaction.response.edit_message(content=help_cmd_msg, view=view)
            else:
                await interaction.response.send_message(content=help_cmd_msg, view=view)
        else:
            curr_page = 1
            help_cmd_msg = f"{help_cmd_msg}```Page {curr_page}/{pages}\n{option_txt[curr_page-1]}```"
            view = NavigationView(cmd_info=cmd_info, option_data=option_txt)
            view.add_item(SelectOption(cmd_info=cmd_info, option_data=option_txt[0]))
            if from_categ_view:
                await interaction.response.edit_message(content=help_cmd_msg, view=view)
            else:
                await interaction.response.send_message(content=help_cmd_msg, view=view)
    else:
        in_grp = cmd_info.parent
        if not in_grp:
            help_cmd_msg = f"**Command**: `{cmd_info.name}`\n**Description**: {desc}"
        else:
            help_cmd_msg = (
                f"**Command**: `{in_grp.name} {cmd_info.name}`\n**Description**: {desc}"
            )

        if from_categ_view:
            await interaction.response.edit_message(content=help_cmd_msg, view=None)
        else:
            await interaction.response.send_message(content=help_cmd_msg)


class NavigationView(View):
    """
    A UI view containing a navigation menu using Buttons from the Discord Bot UI Kit.

    ...

    Attributes
    ----------
    cmd_info : app_commands.Command, optional
        A slash command
    option_data : str, optional
        A list of options to create pages to display from
    category : str, optional
        A category name
    is_categ : bool, optional
        Whether or not the options are a list of commands belonging to a category
    bot : commands.Bot, optional
        The discord bot

    Methods
    -------
    btn_start_callback(interaction, button)
        The callback associated with the Button UI item to return to the first page
    btn_back_callback(interaction, button)
        The callback associated with the Button UI item to go back a page
    btn_forward_callback(interaction, button)
        The callback associated with the Button UI item to go forward a page
    btn_end_callback(interaction, button)
        The callback associated with the Button UI item to go to the last page
    btn_stop_callback(interaction, button)
        The callback associated with the Button UI item to exit the navigation menu
    """

    def __init__(
        self,
        cmd_info: Optional[app_commands.Command] = None,
        option_data: Optional[List[str]] = None,
        category: Optional[str] = None,
        is_categ: Optional[bool] = None,
        bot: Optional[commands.Bot] = None,
    ):
        super().__init__()
        self.option_data = option_data
        self.cmd_info = cmd_info
        self.category = category
        self.is_categ = is_categ
        self.bot = bot

        if self.cmd_info != None:
            desc = self.cmd_info.description
            self.help_cmd_intro = f"**Command**: `{self.cmd_info.name}`\n**Description**: {desc}\n\n**Options**:\n"

        if self.category != None:
            self.help_cmd_intro = f"{self.category}\n"

        if self.option_data != None:
            self.pages = len(self.option_data)
            self.curr_page = 1

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
        if self.is_categ:
            self.add_item(
                SelectOption(
                    option_data=self.option_data[self.curr_page - 1],
                    is_categ=self.is_categ,
                    bot=self.bot,
                )
            )
        else:
            self.add_item(
                SelectOption(
                    cmd_info=self.cmd_info,
                    option_data=self.option_data[self.curr_page - 1],
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
        if self.is_categ:
            self.add_item(
                SelectOption(
                    option_data=self.option_data[self.curr_page - 1],
                    is_categ=self.is_categ,
                    bot=self.bot,
                )
            )
        else:
            self.add_item(
                SelectOption(
                    cmd_info=self.cmd_info,
                    option_data=self.option_data[self.curr_page - 1],
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
        if self.is_categ:
            self.add_item(
                SelectOption(
                    option_data=self.option_data[self.curr_page - 1],
                    is_categ=self.is_categ,
                    bot=self.bot,
                )
            )
        else:
            self.add_item(
                SelectOption(
                    cmd_info=self.cmd_info,
                    option_data=self.option_data[self.curr_page - 1],
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
        if self.is_categ:
            self.add_item(
                SelectOption(
                    option_data=self.option_data[self.curr_page - 1],
                    is_categ=self.is_categ,
                    bot=self.bot,
                )
            )
        else:
            self.add_item(
                SelectOption(
                    cmd_info=self.cmd_info,
                    option_data=self.option_data[self.curr_page - 1],
                )
            )

        help_cmd_msg = f"{self.help_cmd_intro}```Page {self.curr_page}/{self.pages}\n{self.option_data[self.curr_page-1]}```"
        await interaction.response.edit_message(content=help_cmd_msg, view=self)

    @discord.ui.button(style=ButtonStyle.danger, emoji="✖️", custom_id="danger")
    async def btn_stop_callback(self, interaction: discord.Interaction, button: Button):
        msg = interaction.message.content
        await interaction.response.edit_message(content=msg, view=None)


class SingleButtonView(View):
    """
    A UI view containing a single button from the Discord Bot UI Kit.

    ...

    Attributes
    ----------
    cmd_info : app_commands.Command, optional
        A slash command
    option_data : str, optional
        A single option to choose
    is_categ : bool, optional
        Whether or not the option is a command belonging to a category
    bot : commands.Bot, optional
        The discord bot

    Methods
    -------
    btn_choose_callback(interaction, button)
        The callback associated with the Button UI item
    """

    def __init__(
        self,
        cmd_info: Optional[app_commands.Command] = None,
        option_data: Optional[str] = None,
        is_categ: Optional[bool] = None,
        bot: Optional[commands.Bot] = None,
    ):
        self.cmd_info = cmd_info
        self.option_data = option_data
        self.is_categ = is_categ
        self.bot = bot
        super().__init__()

    @discord.ui.button(style=ButtonStyle.success, label="Choose", custom_id="choose")
    async def btn_choose_callback(
        self, interaction: discord.Interaction, button: Button
    ):
        if self.cmd_info != None:
            parse_option = (
                self.option_data.split("-")[0].split(":")[1].split("[")[0].strip()
            )
            param_details = option_details(self.cmd_info, parse_option)
            await interaction.response.edit_message(content=param_details, view=None)
        elif self.is_categ:
            # Because this is a category, option_data will be our single command
            parse_command = self.option_data.split("-")[0].split(":")[1].strip()
            command = self.bot.tree.get_command(parse_command)
            await command_view_helper(command, interaction, from_categ_view=True)


class SelectOption(Select):
    """
    A UI select menu with a list of custom options.

    ...

    Attributes
    ----------
    cmd_info : app_commands.Command, optional
        A slash command
    option_data : str, optional
        A list of options to select from
    is_categ : bool, optional
        Whether or not the options are a list of commands belonging to a category
    is_group : bool, optional
        Whether or not the options are a list of subcommands belonging to a group
    group_info : app_commands.Group, optional
        A parent command
    bot : commands.Bot, optional
        The discord bot

    Methods
    -------
    callback(interaction)
        The callback associated with the Select UI item
    """

    def __init__(
        self,
        cmd_info: Optional[app_commands.Command] = None,
        option_data: Optional[str] = None,
        is_categ: Optional[bool] = False,
        is_group: Optional[bool] = False,
        group_info: Optional[app_commands.Group] = None,
        bot: Optional[commands.Bot] = None,
    ):

        self.option_data = option_data
        self.cmd_info = cmd_info
        self.is_categ = is_categ
        self.is_group = is_group
        self.group_info = group_info
        self.bot = bot

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
        if self.cmd_info != None:
            parse_option = self.values[0].split(":")[1].split("[")[0].strip()
            param_details = option_details(self.cmd_info, parse_option)
            await interaction.response.edit_message(content=param_details, view=None)
        elif self.is_categ:
            parse_command = self.values[0].split(":")[1].strip()
            command = self.bot.tree.get_command(parse_command)
            cmd_type = type(command)
            if cmd_type == app_commands.Command:
                await command_view_helper(command, interaction, from_categ_view=True)
            elif cmd_type == app_commands.Group:
                await group_view_helper(command, interaction, self.bot)
        elif self.is_group:
            parse_command = self.values[0].split(":")[1].strip()
            command = self.group_info.get_command(parse_command)
            await command_view_helper(command, interaction, from_categ_view=True)


class General(commands.Cog):
    """
    A Cog that contains general commands.

    ...

    Attributes
    ----------
    bot : commands.Bot
        The discord bot

    Methods
    -------
    slash_help(interaction,input)
        Learn about commands and supported features
    set_prefix(interaction,prefix)
        Set Prefix
    view_prefix(interaction)
        View Prefix
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: General loaded.")

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
        """
        Learn about commands and supported features

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        input : str, optional
            A command, subcommand, option, or category that you want to view more details about
        """
        # self.bot.help_dict.keys() for all categories
        # self.bot.help_dict.values() for all commands
        slash_commands = [
            command.lower()
            for sub_list in self.bot.help_dict.values()
            for command in sub_list
        ]

        slash_categories = [category.lower() for category in self.bot.help_dict.keys()]

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
                sorted_command_list = sorted(command_list)
                value = ", ".join(sorted_command_list)
                embedMsg.add_field(name=key.upper(), value=value, inline=False)
                command_list.clear()
            # \u2800 is an invisible unicode character, can also maybe use \u200b
            embedMsg.add_field(name="\u2800", value=f"{trailing_text}", inline=False)
            await interaction.response.send_message(embed=embedMsg)
            return None  # exit

        # TODO: split only the first word and hanndle the rest of the input seperately if it exists
        input_params = input.split(" ")
        input_length = len(input_params)
        is_cmd = input_params[0].lower() in slash_commands
        is_categ = input_params[0].lower() in slash_categories

        if not is_cmd and not is_categ:
            await interaction.response.send_message(
                content="Failed to find relevant help for input"
            )
            return None  # exit

        # if a command and category share a name then we'll need to address it
        if is_cmd and is_categ:
            await interaction.response.send_message(
                content="**ALERT**: There is a shared name between a category and command!!!"
            )
            return None  # exit

        # /help command option || /help command subcommand
        if input_length > 1 and is_cmd:
            input_cmd = input_params[0]
            input_add = input_params[1]
            param = None

            cmd_info = self.bot.tree.get_command(input_cmd)
            if type(input_add) == app_commands.Parameter:
                param = cmd_info.get_parameter(input_add)  # returns None if not found
            elif type(input_add) == app_commands.Group:
                pass

            if param != None:
                option_help = option_details(cmd_info, param.name)
                await interaction.response.send_message(content=option_help)
            # if subcommand
            else:
                sub_cmd = cmd_info.get_command(input_add)
                await command_view_helper(sub_cmd, interaction)

        # /help command
        elif is_cmd:
            cmd_info = self.bot.tree.get_command(input)
            cmd_type = type(cmd_info)
            if cmd_type == app_commands.Command:
                await command_view_helper(cmd_info, interaction)
            elif cmd_type == app_commands.Group:
                await group_view_helper(cmd_info, interaction, self.bot)
        # /help category
        elif is_categ:
            command_list = []
            for key in self.bot.help_dict.keys():
                if key.lower() == input_params[0].lower():
                    command_list = sorted(self.bot.help_dict[key])
                    break
            help_cmd_msg = f"{input_params[0].capitalize()}\n"

            count = 0
            page_content = []
            for command in command_list:
                count += 1
                cmd_info = self.bot.tree.get_command(command)
                cmd_desc = cmd_info.description

                # description exists
                if len(cmd_desc) > 0:
                    page_content.append(f"{count} : {cmd_info.name} - {cmd_desc}")
                else:
                    page_content.append(f"{count} : {cmd_info.name}")
            option_txt = [
                "\n".join(page_content[i : i + 10])
                for i in range(0, len(page_content), 10)
            ]

            pages = len(option_txt)

            # modify to work with category, encapsulate cmd logic, selectoption.values[0] pass ass cmd
            # view won't know cmd_info so pass reference to bot instead, update cmd_helper func
            if pages == 1 and count == 1:
                view = SingleButtonView(
                    option_data=option_txt[0], is_categ=is_categ, bot=self.bot
                )
                help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
                await interaction.response.send_message(content=help_cmd_msg, view=view)
            elif pages == 1 and count <= 10:
                view = View()
                view.add_item(
                    SelectOption(
                        option_data=option_txt[0], is_categ=is_categ, bot=self.bot
                    )
                )
                help_cmd_msg = f"{help_cmd_msg}```{option_txt[0]}```"
                await interaction.response.send_message(content=help_cmd_msg, view=view)
            else:
                curr_page = 1
                help_cmd_msg = f"{help_cmd_msg}```Page {curr_page}/{pages}\n{option_txt[curr_page-1]}```"
                view = NavigationView(
                    option_data=option_txt, is_categ=is_categ, bot=self.bot
                )
                view.add_item(
                    SelectOption(
                        option_data=option_txt[0], is_categ=is_categ, bot=self.bot
                    )
                )
                await interaction.response.send_message(content=help_cmd_msg, view=view)
            # reuse nav view and is_cmd code
            # selecting a command will lead to nav view with the command selected

    prefix_group = app_commands.Group(
        name="prefix", description="Manage command prefix", extras={"module": "General"}
    )
    # app_commands.checks.has_role for guild permissions?
    @prefix_group.command(name="set", description="Set Prefix")
    @app_commands.describe(prefix="[STRING] New Prefix")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_prefix(self, interaction: discord.Interaction, prefix: str):
        """
        Set Prefix

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        prefix : str
            A guild's new prefix
        """
        db = SQL()
        if not db.set_prefix(interaction.guild_id, prefix):
            await interaction.response.send_message(f"Unable to change prefix.")
        else:
            await interaction.response.send_message(
                f"Prefix successfully changed to `{prefix}`"
            )
        db.close()

    @prefix_group.command(name="view", description="View Prefix")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def view_prefix(self, interaction: discord.Interaction):
        """
        View Prefix

        ...

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction caused by a user performing a slash command
        """
        db = SQL()
        prefix = db.get_prefix(interaction.guild_id)
        if not prefix:
            await interaction.response.send_message(f"Unable to retrieve prefix.")
        else:
            await interaction.response.send_message(
                f"Prefix currently set to `{prefix}`"
            )
        db.close()


async def setup(bot):
    await bot.add_cog(General(bot))

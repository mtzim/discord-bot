import os
from typing import Optional
import discord
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands
from gpt_core.gpt_mode import ChatGPT
from gpt_core.gpt_utils import setup_personality


class ChatBot(commands.Cog):

    MODULE_NAME = {
        "module": f"{os.path.splitext(os.path.basename(__file__))[0].capitalize()}"
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.chat_gpt = ChatGPT()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: {self.MODULE_NAME['module']} loaded.")

    @app_commands.command(
        name="chat",
        description="Talk to the chatbot with text",
        extras=MODULE_NAME,
    )
    @app_commands.describe(input="[STRING] Ask or tell the chatbot something")
    async def chatbot_text(self, interaction: discord.Interaction, input: str):
        await interaction.response.defer()
        response = self.chat_gpt.gpt_text(input)
        # embed = discord.Embed(color=discord.Color.blue())
        # embed.add_field(name="\u2800", value=f"{response}", inline=False)
        # print(f"\n{response}\n")
        # print(response)

        # TODO: Implement better workaround for handling reponses that exceed discord char limit
        # Consider between pages with nav view or chain msgs with better formatting
        resp_len = len(response)
        discord_char_limit = 1800
        if resp_len > discord_char_limit:
            # Back up until space
            while response[discord_char_limit - 1] != " ":
                discord_char_limit -= 1
            split_response = list()
            split_response.append(f"{response[:discord_char_limit]}")
            split_response.append(f"{response[discord_char_limit:]}")
            await interaction.followup.send(content=split_response[0])
            await interaction.followup.send(content=split_response[1])
        else:
            await interaction.followup.send(content=response)

    @app_commands.command(
        name="prompt",
        description="Change the prompt of the chatbot",
        extras=MODULE_NAME,
    )
    @app_commands.describe(input="[STRING] New prompt to set")
    async def chatbot_prompt(self, interaction: discord.Interaction, input: str):
        await interaction.response.defer(ephemeral=True)

        # Check if the invoker is the bot owner
        command_invoker = interaction.user.id
        bot_owner = interaction.client.application.owner.id

        if command_invoker == bot_owner:
            self.chat_gpt.messages = setup_personality(input)
            await interaction.followup.send(content="Prompt updated")
        else:
            await interaction.followup.send(
                content="Only the bot owner can change the prompt"
            )

    gpt_settings_group = app_commands.Group(
        name="modelsettings",
        description="Manage GPT model settings",
        extras=MODULE_NAME,
    )

    @gpt_settings_group.command(
        name="set",
        description="Set chatbot's GPT model settings",
    )
    @app_commands.describe(
        conv_limit="[INT] Limit the model's context length",
        model="[STRING] ID of the model to use",
        temperature="[FLOAT] (0.0 to 2.0) Increase for output to be random, Decrease for output to be more deterministic",
        max_tokens="[INT] (Less than 4096) The maximum number of tokens to generate in the chat completion",
        pp="[FLOAT] (-2.0 to 2.0) Increase or Decrease model's likelihood to talk about new topics",
        fp="[FLOAT] (-2.0 to 2.0) Increase or Decrease model's likelihood to repeat the same line verbatim",
        stop="[STRING] Up to 4 sequences where the API will stop generating further tokens",
    )
    @app_commands.choices(
        model=[
            Choice(name="gpt-4", value=1),
            Choice(name="gpt-4-0314", value=2),
            Choice(name="gpt-4-32k", value=3),
            Choice(name="gpt-4-32k-0314", value=4),
            Choice(name="gpt-3.5-turbo", value=5),
            Choice(name="gpt-3.5-turbo-0301", value=6),
        ]
    )
    async def set_chatbot_parameters(
        self,
        interaction: discord.Interaction,
        conv_limit: Optional[int] = None,
        model: Optional[Choice[int]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        pp: Optional[float] = None,
        fp: Optional[float] = None,
        stop: Optional[str] = None,
    ):
        updated = False
        if conv_limit is not None:
            self.chat_gpt.conversation_limit = conv_limit
            updated = True
        if model is not None:
            self.chat_gpt.model = model.name
            updated = True
        if temperature is not None and temperature >= 0 and temperature <= 2.0:
            self.chat_gpt.temperature = temperature
            updated = True
        if max_tokens is not None and max_tokens <= 4096:
            self.chat_gpt.max_tokens = max_tokens
            updated = True
        if pp is not None and pp >= -2.0 and pp <= 2.0:
            self.chat_gpt.presence_penalty = pp
            updated = True
        if fp is not None and fp >= -2.0 and fp <= 2.0:
            self.chat_gpt.frequency_penalty = fp
            updated = True
        if stop is not None:
            self.chat_gpt.stop = stop
            updated = True

        if updated:
            await interaction.response.send_message(
                content="Model settings updated", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                content="No model settings were changed, select a parameter to update",
                ephemeral=True,
            )

    @gpt_settings_group.command(
        name="view",
        description="View chatbot's GPT model settings",
    )
    async def view_chatbot_parameters(self, interaction: discord.Interaction):
        conv_limit = self.chat_gpt.conversation_limit
        model = self.chat_gpt.model
        temperature = self.chat_gpt.temperature
        max_tokens = self.chat_gpt.max_tokens
        pp = self.chat_gpt.presence_penalty
        fp = self.chat_gpt.frequency_penalty
        stop = self.chat_gpt.stop

        await interaction.response.send_message(
            content=f"Conversation limit: `{conv_limit}`\nModel: `{model}`\nTemperature: `{temperature}`\nMax tokens: `{max_tokens}`\nPresence penalty: `{pp}`\nFrequency penalty: `{fp}`\nStop: `{stop}`"
        )


async def setup(bot):
    await bot.add_cog(ChatBot(bot))

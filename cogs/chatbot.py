import os
import discord
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


async def setup(bot):
    await bot.add_cog(ChatBot(bot))

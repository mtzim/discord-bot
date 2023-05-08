import os
import discord
from discord.ext import commands
from discord import app_commands
from gpt_core.gpt_mode import ChatGPT


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


async def setup(bot):
    await bot.add_cog(ChatBot(bot))

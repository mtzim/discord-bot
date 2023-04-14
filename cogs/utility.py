import discord
from discord.ext import commands
from typing import List, Optional
from datetime import date, datetime
from discord import app_commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: Utility loaded.")

    @app_commands.command(
        description=f"Display avatar of a user",
        extras={"module": "Utility"},
    )
    @app_commands.describe(user="[USER] user")
    async def avatar(
        self, interaction: discord.Interaction, user: Optional[discord.User] = None
    ):
        """
        Displays the full resolution of the user's avatar

        Use discord.utils.get(ctx.bot.users,mention=user) for guild_member
        instead if you want the user's global avatar even if the user has set
        a guild avatar.
        """
        if not user:
            user = interaction.user
        embed = discord.Embed()
        embed.set_image(url=user.display_avatar.url)
        embed.title = f"{user}"
        embed.description = f"[Display Avatar]({user.display_avatar.url})"
        # embed.set_footer(text=f"?avatar invoked by {ctx.author}")
        # await ctx.message.delete()
        await interaction.response.send_message(
            allowed_mentions=discord.AllowedMentions.none(), embed=embed
        )

    @app_commands.command(
        description=f"Display info about a user",
        extras={"module": "Utility"},
    )
    @app_commands.describe(user="[USER] user to show")
    async def userinfo(
        self, interaction: discord.Interaction, user: Optional[discord.User] = None
    ):
        """Displays various information about a user"""

        if not user:
            user = interaction.user
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{user}", icon_url=f"{user.display_avatar.url}")
        embed.set_thumbnail(url=f"{user.display_avatar.url}")

        role_text = self.list_roles(user.roles)
        joined_at_text = self.format_date(user.joined_at)
        created_at_text = self.format_date(user.created_at)

        embed.add_field(name=f"ID", value=user.id, inline=False)
        embed.add_field(name=f"Mention", value=user.mention, inline=False)
        embed.add_field(name=f"Status", value=user.status, inline=False)
        embed.add_field(name=f"Roles", value=role_text, inline=False)
        embed.add_field(name=f"Joined", value=joined_at_text, inline=False)
        embed.add_field(name=f"Created", value=created_at_text, inline=False)
        await interaction.response.send_message(
            allowed_mentions=discord.AllowedMentions.none(), embed=embed
        )

    # Excludes @everyone role at index 0
    def list_roles(self, roles: List[discord.Role]) -> str:
        role_list = []
        for role in roles[1:]:
            name = f"{role.mention}"
            role_list.append(name)
        value = ", ".join(role_list)
        return value

    # Formats date to YYYY/MM/DD
    def format_date(self, date: datetime):
        return date.strftime("%Y/%m/%d")


async def setup(bot):
    await bot.add_cog(Utility(bot))

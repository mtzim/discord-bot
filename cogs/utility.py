import discord
from discord.ext import commands
from typing import List, Optional
from datetime import date, datetime


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"* Cog: Utility loaded.")

    @commands.command(help="Usage: `?avatar <USER>`")
    async def avatar(self, ctx: commands.Context, user):
        """
        Displays the full resolution of the user's avatar

        Use discord.utils.get(ctx.bot.users,mention=user) for guild_member
        instead if you want the user's global avatar even if the user has set
        a guild avatar.
        """
        guild_member = discord.utils.get(ctx.guild.members, mention=user)
        embed = discord.Embed()
        embed.set_image(url=guild_member.display_avatar.url)
        embed.title = f"{guild_member}"
        embed.description = f"[Display Avatar]({guild_member.display_avatar.url})"
        # embed.set_footer(text=f"?avatar invoked by {ctx.author}")
        # await ctx.message.delete()
        await ctx.reply(allowed_mentions=discord.AllowedMentions.none(), embed=embed)

    @commands.command(help="Usage: `?userinfo <USER>`")
    async def userinfo(self, ctx: commands.Context, user):
        """Displays various information about a user"""
        guild_member = discord.utils.get(ctx.guild.members, mention=user)
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(
            name=f"{guild_member}", icon_url=f"{guild_member.display_avatar.url}"
        )
        embed.set_thumbnail(url=f"{guild_member.display_avatar.url}")

        role_text = self.list_roles(guild_member.roles)
        joined_at_text = self.format_date(guild_member.joined_at)
        created_at_text = self.format_date(guild_member.created_at)

        embed.add_field(name=f"ID", value=guild_member.id, inline=False)
        embed.add_field(name=f"Mention", value=guild_member.mention, inline=False)
        embed.add_field(name=f"Status", value=guild_member.status, inline=False)
        embed.add_field(name=f"Roles", value=role_text, inline=False)
        embed.add_field(name=f"Joined", value=joined_at_text, inline=False)
        embed.add_field(name=f"Created", value=created_at_text, inline=False)
        await ctx.reply(allowed_mentions=discord.AllowedMentions.none(), embed=embed)

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

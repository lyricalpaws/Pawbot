import time
import discord
import psutil
import os
import asyncio

from discord.ext import commands
from datetime import datetime
from utils import repo, default


class Information:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    def get_bot_uptime(self, *, brief=False):
        now = datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
            else:
                fmt = '{h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h}h {m}m {s}s'
            if days:
                fmt = '{d}d ' + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        message = await ctx.send("Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong   |   {int(ping)}ms")

    @commands.command(aliases=['joinme', 'join', 'botinvite'])
    async def invite(self, ctx):
        """ Invite me to your server """
        await ctx.send(f"**{ctx.author.name}**, use this URL to invite me\n<https://discordapp.com/oauth2/authorize?client_id=460383314973556756&scope=bot&permissions=469888118>")

    @commands.command(aliases=['supportserver', 'feedbackserver'])
    async def botserver(self, ctx):
        """ Get an invite to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 353684556848562176:
            return await ctx.send(f"**{ctx.author.name}**, you can join here! 🍻\n<{repo.invite}>")

        await ctx.send(f"**{ctx.author.name}**, this is my home.")

    @commands.command(aliases=['info', 'stats', 'status'])
    @commands.guild_only()
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = round(len(self.bot.users) / len(self.bot.guilds))

        embed = discord.Embed(title=f"About **{ctx.bot.user.name}** | **{repo.version}**", colour=ctx.me.colour, url="https://discordapp.com/oauth2/authorize?client_id=460383314973556756&scope=bot&permissions=469888118",)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Uptime", value=self.get_bot_uptime(), inline=False)
        embed.add_field(name="Developer", value="Paws#0001", inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} (average: {avgmembers} users/server )", inline=True)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)
        embed.add_field(name="Support", value=f"[Here]({repo.invite})", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=249742)
        embed.description = f"Avatar to **{user.name}**\nClick [here]({user.avatar_url}) to get image"
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, user: discord.Member = None):
        """ Check when a user joined the current server """
        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=249742)
        embed.set_thumbnail(url=user.avatar_url)
        embed.description = f'**{user}** joined **{ctx.guild.name}**\n{default.date(user.joined_at)}'
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def server(self, ctx):
        """ Check info about current server """
        if ctx.invoked_subcommand is None:
            findbots = sum(1 for member in ctx.guild.members if member.bot)

            embed = discord.Embed(colour=249742)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
            embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
            embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="Bots", value=findbots, inline=True)
            embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
            embed.add_field(name="Region", value=ctx.guild.region, inline=True)
            embed.add_field(name="Created", value=default.date(ctx.guild.created_at), inline=True)
            await ctx.send(content=f"ℹ information about **{ctx.guild.name}**", embed=embed)

    @commands.command()
    async def user(self, ctx, user: discord.Member = None):
        """ Get user information """
        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=249742)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Full name", value=user, inline=True)

        if hasattr(user, "nick"):
            embed.add_field(name="Nickname", value=user.nick, inline=True)
        else:
            embed.add_field(name="Nickname", value="None", inline=True)

        embed.add_field(name="Account created", value=default.date(user.created_at), inline=True)

        if hasattr(user, "joined_at"):
            embed.add_field(name="Joined this server", value=default.date(user.joined_at), inline=True)

        await ctx.send(content=f"ℹ About **{user.id}**", embed=embed)

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, time, *, question):
        """
        Creates a poll
        """
        await ctx.message.delete()
        time = int(time)
        pollmsg = await ctx.send(f"{ctx.message.author.mention} created a poll that will end after {time} seconds!\n**{question}**\n\nReact with :thumbsup: or :thumbsdown: to vote!")
        await pollmsg.add_reaction('👍')
        await pollmsg.add_reaction('👎')
        await asyncio.sleep(time)
        reactiongrab = await ctx.channel.get_message(pollmsg.id)
        for reaction in reactiongrab.reactions:
            if reaction.emoji == str('👍'):
                upvote_count = reaction.count
            else:
                if reaction.emoji == str('👎'):
                    downvote_count = reaction.count
                else:
                    pass
        await pollmsg.edit(content=f"{ctx.message.author.mention} created a poll that will end after {time} seconds!\n**{question}**\n\nTime's up!\n👍 = {upvote_count-1}\n\n👎 = {downvote_count-1}")


def setup(bot):
    bot.add_cog(Information(bot))

import asyncio
from discord.ext import commands
import logging
import traceback
from discord import Forbidden, NotFound, HTTPException

from .utils import discord_utils as utils


class Administrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('root.cogs.administrator')

    @commands.check(utils.is_owner)
    @commands.command(aliases=['kill'])
    async def _logout(self, ctx):
        self.log.info("Initiating logout phase")

        try:
            await asyncio.wait_for(self.bot.pool.close(), timeout=5.0)
        except asyncio.TimeoutError:
            self.log.error("Force send terminate() on connection pool")

        self.log.info("Connection pool closed")
        await self.bot.logout()

    @commands.check(utils.is_owner)
    @commands.command(aliases=['load'])
    async def load_cog(self, ctx, cog: str):
        cog = f'{self.bot.cog_path}{cog}'
        try:
            self.bot.load_extension(cog)
        except:
            await self.bot.embed_print(ctx, title='COG LOAD ERROR', color='red',
                                       description=f'`{cog}` not found')
            return
        await self.bot.embed_print(ctx, title='COG COMMAND', color='green',
                                   description=f'Loaded `{cog}` successfully')

    @commands.check(utils.is_owner)
    @commands.command(aliases=['unload'])
    async def unload_cog(self, ctx, cog: str):
        cog = f'{self.bot.cog_path}{cog}'
        try:
            self.bot.unload_extension(cog)
        except:
            await self.bot.embed_print(ctx, title='COG LOAD ERROR', color='red',
                                       description=f'`{cog}` not found')
            return
        await self.bot.embed_print(ctx, title='COG COMMAND', color='green',
                                   description=f'Unloaded `{cog}` successfully')

    @commands.check(utils.is_owner)
    @commands.command(aliases=['re'])
    async def re_load(self, ctx, cog: str):
        cog = f'{self.bot.cog_path}{cog}'

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except:
            await self.bot.embed_print(ctx, title='COG LOAD ERROR', color='red',
                                       description=f'`{cog}` not found')
            return
        await self.bot.embed_print(ctx, title='COG COMMAND', color='green',
                                   description=f'Reloaded `{cog}` successfully')

    @commands.check(utils.is_owner)
    @commands.command()
    async def re_run(self, ctx, *, args):
        """
        Command method used to reload a cog and run a command afterwards. This simply calls
        two command methods so that you do not have to type the commands twice in Discord.

        Usage: {prefix} {cog to reload} {command to run} {args}

        Parameters
        ----------
        ctx : discord.ext.commands.Context
            Represents the context in which a command is being invoked under.
        args : str
            String containing the cog to reload and command to run
        """
        # Parse the arguments
        parsed_command = args.split(' ', 2)

        # Get the commands to run
        reload_cog = self.bot.get_command('re_load')
        run_command = self.bot.get_command(parsed_command[1])
        if run_command is None:
            await self.bot.embed_print(ctx, title='COMMAND ERROR', color='red',
                                       description=f'Command `{parsed_command[1]}` not found')
            return

        # Run commands
        await ctx.invoke(reload_cog, parsed_command[0])
        await ctx.invoke(run_command, parsed_command[-1])

    @commands.check(utils.is_owner)
    @commands.command()
    async def list_cogs(self, ctx):
        output = ''
        for i in self.bot.cog_tupe:
            output += f"`{i.split('.')[-1]}`\n"
        await self.bot.embed_print(ctx, title='COG LIST', description=output)

    @commands.check(utils.is_owner)
    @commands.command()
    async def set_debug(self, ctx, status):
        if status.lower() in ('f', 'false'):
            self.bot.debug = False
            await self.bot.embed_print(ctx, color='green', description='Debugging disabled')
        elif status.lower() in ('t', 'true'):
            self.bot.debug = True
            await self.bot.embed_print(ctx, color='green', description='Debugging enabled')
        else:
            await self.bot.embed_print(ctx, color='red', description='Invalid bool')


def setup(bot):
    bot.add_cog(Administrator(bot))

from discord.ext import commands
import logging
import json
import traceback
from .utils import discord_utils as utils
from .utils import discord_arg_parser as argparse

class BotConfigurator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.db_conn
        self.log = logging.getLogger('root.cogs.bot_setup')

    @commands.check(utils.is_owner)
    @commands.group()
    async def setup(self, ctx):
        pass

    @setup.command(name='roles')
    async def setup_roles(self, ctx, *, args=None):
        # Get current roles supported
        rows = self.db_conn.fetch_table('helpers')
        if not rows:
            await self.bot.embed_print(ctx, title='SETUP: Roles', color='green',
                                   description=f'No roles currently configured')
        else:
            # TODO: Add code for printing out the roles
            print("TODO")

        #resp = await self.bot.wait_for('message')
        msg = "Would you like to add roles, clear roles, or cancel?"
        panel = await self.bot.embed_print(ctx, title='SETUP: Roles', color='green',
                                           description=f'{msg}', _return=True)
        print(dir(panel))
        # TODO: Add the rest of your emojis here

def setup(bot):
    bot.add_cog(BotConfigurator(bot))


#cur.execute("INSERT INTO friends(name) VALUES ('Tom')")
        # self.db_conn.cursor.execute("INSERT INTO helpers VALUES (11123,'Jason')")
        # self.db_conn.conn.commit()
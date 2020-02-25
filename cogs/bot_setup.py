import asyncio
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
        self.zbp_server = self.bot.get_guild(self.bot.settings.zbp_server)
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
            await self.bot.embed_print(ctx, color='blue',
                                   description=f'No roles currently configured')
        else:
            # TODO: Add code for printing out the roles
            print("TODO")

        # Display the menu for this command
        msg = (f"Would you like to:\n"
               f"{self.bot.settings.emojis['add']} `Add Roles`\n"
               f"{self.bot.settings.emojis['reset']} `Clear Roles`\n"
               f"{self.bot.settings.emojis['cancel']} `Cancel Operation`")
        embed_out = await self.bot.embed_print(ctx, title='Role Setup Menu', color='blue',
                                           description=f'{msg}', _return=True)
        panel = await ctx.send(embed=embed_out)
        raw_emojis = (
            f"{self.bot.settings.emojis['add']}",
            f"{self.bot.settings.emojis['reset']}",
            f"{self.bot.settings.emojis['cancel']}"
        )
        for raw_emoji in raw_emojis:
            await panel.add_reaction(raw_emoji)


        # Interpret the actions to be taken
        def check(reaction, user):
            if user != ctx.message.author:
                return False
            if str(reaction.emoji) in raw_emojis:
                return True
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', check=check, timeout=60.0)
            await reaction.remove(user)
        except asyncio.TimeoutError:
            await panel.clear()
        finally:
            await panel.clear_reactions()
        if str(reaction.emoji) == f"{self.bot.settings.emojis['add']}":
            await self.set_roles(ctx)

    async def set_roles(self, ctx):
        #self.zbp_server
        # TODO: Print roles with numbers and have the user pick them one at a time
        role_objects = ( role for role in self.zbp_server.roles )
        for i in range(0, 10):
            number = f'rcs{str(i)}'
            await ctx.send(f'{self.bot.settings.emojis[f"{number}"]}')

def setup(bot):
    bot.add_cog(BotConfigurator(bot))


#cur.execute("INSERT INTO friends(name) VALUES ('Tom')")
        # self.db_conn.cursor.execute("INSERT INTO helpers VALUES (11123,'Jason')")
        # self.db_conn.conn.commit()
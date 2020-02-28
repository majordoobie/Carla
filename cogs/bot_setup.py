from math import ceil

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
            await self.bot.embed_print(ctx, color='info',
                                       description=f'No roles currently configured')
        else:
            # TODO: Add code for printing out the roles
            print("TODO")

        # Display the menu for this command
        msg = (f"Would you like to:\n"
               f"{self.bot.settings.emojis['add']} `Add Roles`\n"
               f"{self.bot.settings.emojis['reset']} `Clear Roles`\n"
               f"{self.bot.settings.emojis['cancel']} `Cancel Operation`")
        embed_out = await self.bot.embed_print(ctx, title='Role Setup Menu', color='info',
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
        def check(reaction, user):
            if user != ctx.message.author:
                return False
            if str(reaction.emoji) in raw_emojis:
                return True
        # TODO: You are here need to finish getting the page working
        emoji = self.bot.settings.emojis
        panel = ''
        roles_dict = {}
        roles_list = []
        indexer = {}
        for role in self.bot.zulu_server.roles:
            if role.name == '@everyone':
                continue
            roles_dict[role.name] = {
                'name': role.name,
                'role': role,
                'picked': False
            }
            roles_list.append(role.name)

        # Sort list
        roles_list.sort(key=lambda x: x.lower())

        # Get range blocks
        blocks = ceil(len(roles_list) / 10)
        for block in range(1, blocks+1):
            indexer[str(block)] = ((block * 10 - 10), (block * 10 - 1))

        iterate = True
        index = 1
        while iterate:
            block = indexer[str(index)]
            sector = roles_list[block[0]:block[1]]
            panel = ''
            for idx, role_name in enumerate(sector):
                number = f'rcs{str(idx + 1)}'
                if roles_dict[role_name]['picked']:
                    mark = 'checked'
                else:
                    mark = 'unchecked'
                panel += f'{emoji[number]} {emoji[mark]} {role_name}\n'
            display = await self.bot.embed_print(ctx, description=panel, _return=True)
            display = await ctx.send(embed=display)
            for idx in range(block[0], block[1]):
                number = f'rcs{str(idx + 1)}'
                await display.add_reaction(emoji[number])
            await display.add_reaction(emoji['delete'])
            await display.add_reaction(emoji['save'])
            await display.add_reaction(emoji['right'])
            return

        return
        # for index, block in enumerate(blocks):
        #
        # for index, role in enumerate(self.bot.zulu_server.roles[0:40]):
        #     num = f'rcs{str(index+1)}'
        #     panel += f'{emoji[num]} {emoji["checked"]} {role.name}\n'
        # await self.bot.embed_print(ctx, description=panel)
        #
        # for i in range(0, 10):
        #     number = f'rcs{str(i)}'
        #     await ctx.send(f'{self.bot.settings.emojis[f"{number}"]}')

def setup(bot):
    bot.add_cog(BotConfigurator(bot))


#cur.execute("INSERT INTO friends(name) VALUES ('Tom')")
        # self.db_conn.cursor.execute("INSERT INTO helpers VALUES (11123,'Jason')")
        # self.db_conn.conn.commit()
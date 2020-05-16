from math import ceil

import asyncio
from discord.ext import commands
import logging
import json
import traceback
from utils import discord_utils as utils
from utils import discord_arg_parser as argparse

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
        rows = self.db_conn.fetch_table('role_sync')

        # Send out the initial list of members
        if not rows:
            current_config = await self.bot.embed_print(ctx, color='info',
                                                        description=f'No roles currently configured',
                                                        _return=True)
            current_selections = await ctx.send(embed=current_config)
        else:
            panel = '**Currently configured roles:**\n'
            for row in rows:
                panel += f'{row[1]}\n'
            current_config = await self.bot.embed_print(ctx, color='info',
                                                        description=panel, _return=True)
            current_selections = await ctx.send(embed=current_config)

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
            await panel.delete()
            await self.set_roles(ctx)
        elif str(reaction.emoji) == f"{self.bot.settings.emojis['cancel']}":
            await panel.delete()
            return
        elif str(reaction.emoji) == f"{self.bot.settings.emojis['reset']}":
            embed_out = await self.bot.embed_print(ctx, color='success',
                                                    description='Cleared!', _return=True)
            new_current = await self.bot.embed_print(ctx, color='info',
                                                     description=f'No roles currently configured',
                                                     _return=True)
            await current_selections.edit(embed=new_current)
            await panel.edit(embed=embed_out)
            self.db_conn.cursor.execute('DELETE FROM role_sync')
            self.db_conn.conn.commit()

    async def set_roles(self, ctx, role_li    def __init__(self, bot):
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
        rows = self.db_conn.fetch_table('role_sync')

        # Send out the initial list of members
        if not rows:
            current_config = await self.bot.embed_print(ctx, color='info',
                                                        description=f'No roles currently configured',
                                                        _return=True)
            current_selections = await ctx.send(embed=current_config)
        else:
            panel = '**Currently configured roles:**\n'
            for row in rows:
                panel += f'{row[1]}\n'
            current_config = await self.bot.embed_print(ctx, color='info',
                                                        description=panel, _return=True)
            current_selections = await ctx.send(embed=current_config)

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
            await panel.delete()
            await self.set_roles(ctx)
        elif str(reaction.emoji) == f"{self.bot.settings.emojis['cancel']}":
            await panel.delete()
            return
        elif str(reaction.emoji) == f"{self.bot.settings.emojis['reset']}":
            embed_out = await self.bot.embed_print(ctx, color='success',
                                                    description='Cleared!', _return=True)
            new_current = await self.bot.embed_print(ctx, color='info',
                                                     description=f'No roles currently configured',
                                                     _return=True)
            await current_selections.edit(embed=new_current)
            await panel.edit(embed=embed_out)
            self.db_conn.cursor.execute('DELETE FROM role_sync')
            self.db_conn.conn.commit()

    async def set_roles(self, ctx, role_list_panel):
        # Set the variable needed to track the information
        emoji = self.bot.settings.emojis
        panel = ''
        roles_dict = {}         # {role1: {}, role2: {}}
        roles_list = []         # [role1, role2]
        indexer = {}            # {'1': (0, 9), '2': (10, 19)}
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
            # {'1': (0, 9), '2': (10, 19)}
            indexer[str(block)] = ((block * 10 - 10), (block * 10 - 1))

        # Get the first panel and msg object
        panel = get_panel_embed(roles_list[0:9], roles_dict, emoji, count=f'1/{len(indexer)}')
        embed_panel = await self.bot.embed_print(ctx, description=panel, _return=True)
        msg_output = await ctx.send(embed=embed_panel)
        await set_buttons(ctx, msg_output, emoji)

        # Create the check for the wait for
        def check(reaction, user):
            """A couple checks to make sure we stay complient"""
            # Test that only the user executing the command
            if not ctx.author.id == user.id:
                return False
            # Make sure that the reaction is for the correct message
            if not msg_output.id == reaction.message.id:
                return False
            # Make sure we ignore the bot
            if user.bot:
                return False
            return True

        # After first message is out we can focus on using it
        iterate = True
        index = 1
        while index <= len(indexer):
            if index == len(indexer):
                index = 0
            try:
                # Wait for the user interaction
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60, check=check)
                # Clear the pick so it looks nicer
                await msg_output.remove_reaction(reaction, user)

                # If role was picked
                if reaction.emoji.name.startswith('rcs'):
                    num = reaction.emoji.name.lstrip('rcs')                 # Strips the num from 'rcs#'
                    role_set = roles_list[indexer[str(index)][0]:indexer[str(index)][1]]  # takes the role set
                    chosen_role = role_set[int(num) - 1]
                    # Modify the dictionary
                    if roles_dict[chosen_role]['picked']:
                        roles_dict[chosen_role]['picked'] = False
                    else:
                        roles_dict[chosen_role]['picked'] = True
                elif reaction.emoji.name == 'delete':
                    await msg_output.delete()
                    return
                elif reaction.emoji.name == 'right':
                    index += 1
                elif reaction.emoji.name == 'save':
                    saved_data = []
                    for k, v in roles_dict.items():
                        if v['picked']:
                            try:
                                self.db_conn.cursor.execute('INSERT INTO role_sync VALUES (?,?)',
                                                            (v['role'].id, v['role'].name))
                            except:
                                pass
                    self.db_conn.conn.commit()
                    embed = await self.bot.embed_print(ctx, description='Saved!', _return=True, color='success')
                    await msg_output.clear_reactions()
                    await msg_output.edit(embed=embed)

                    # Set the new panel for selected users
                    rows = self.db_conn.fetch_table('role_sync')
                    panel = '**Newly configured roles:**\n'
                    #TODO: MOve this up a level
                    for row in rows:
                        panel += f'{row[1]}\n'
                    new_current = await self.bot.embed_print(ctx, color='info',
                                                             description=panel,
                                                             _return=True)
                    #await current_selections.edit(embed=new_current)
                    return

                # Get a new panel
                block = indexer[str(index)]                 # {'1': (0, 9)}
                role_names = roles_list[block[0]:block[1]]  # roles_list[0, 9]
                panel = get_panel_embed(role_names, roles_dict, emoji, count=f'{index}/{len(indexer)}')
                embed_panel = await self.bot.embed_print(ctx, description=panel, _return=True)
                await msg_output.edit(embed=embed_panel)

            except asyncio.TimeoutError:
                await msg_output.clear_reactions()
# st_panel):
#         # Set the variable needed to track the information
#         emoji = self.bot.settings.emojis
#         panel = ''
#         roles_dict = {}         # {role1: {}, role2: {}}
#         roles_list = []         # [role1, role2]
#         indexer = {}            # {'1': (0, 9), '2': (10, 19)}
#         for role in self.bot.zulu_server.roles:
#             if role.name == '@everyone':
#                 continue
#             roles_dict[role.name] = {
#                 'name': role.name,
#                 'role': role,
#                 'picked': False
#             }
#             roles_list.append(role.name)
#
#         # Sort list
#         roles_list.sort(key=lambda x: x.lower())
#
#         # Get range blocks
#         blocks = ceil(len(roles_list) / 10)
#         for block in range(1, blocks+1):
#             # {'1': (0, 9), '2': (10, 19)}
#             indexer[str(block)] = ((block * 10 - 10), (block * 10 - 1))
#
#         # Get the first panel and msg object
#         panel = get_panel_embed(roles_list[0:9], roles_dict, emoji, count=f'1/{len(indexer)}')
#         embed_panel = await self.bot.embed_print(ctx, description=panel, _return=True)
#         msg_output = await ctx.send(embed=embed_panel)
#         await set_buttons(ctx, msg_output, emoji)
#
#         # Create the check for the wait for
#         def check(reaction, user):
#             """A couple checks to make sure we stay complient"""
#             # Test that only the user executing the command
#             if not ctx.author.id == user.id:
#                 return False
#             # Make sure that the reaction is for the correct message
#             if not msg_output.id == reaction.message.id:
#                 return False
#             # Make sure we ignore the bot
#             if user.bot:
#                 return False
#             return True
#
#         # After first message is out we can focus on using it
#         iterate = True
#         index = 1
#         while index <= len(indexer):
#             if index == len(indexer):
#                 index = 0
#             try:
#                 # Wait for the user interaction
#                 reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60, check=check)
#                 # Clear the pick so it looks nicer
#                 await msg_output.remove_reaction(reaction, user)
#
#                 # If role was picked
#                 if reaction.emoji.name.startswith('rcs'):
#                     num = reaction.emoji.name.lstrip('rcs')                 # Strips the num from 'rcs#'
#                     role_set = roles_list[indexer[str(index)][0]:indexer[str(index)][1]]  # takes the role set
#                     chosen_role = role_set[int(num) - 1]
#                     # Modify the dictionary
#                     if roles_dict[chosen_role]['picked']:
#                         roles_dict[chosen_role]['picked'] = False
#                     else:
#                         roles_dict[chosen_role]['picked'] = True
#                 elif reaction.emoji.name == 'delete':
#                     await msg_output.delete()
#                     return
#                 elif reaction.emoji.name == 'right':
#                     index += 1
#                 elif reaction.emoji.name == 'save':
#                     saved_data = []
#                     for k, v in roles_dict.items():
#                         if v['picked']:
#                             try:
#                                 self.db_conn.cursor.execute('INSERT INTO role_sync VALUES (?,?)',
#                                                             (v['role'].id, v['role'].name))
#                             except:
#                                 pass
#                     self.db_conn.conn.commit()
#                     embed = await self.bot.embed_print(ctx, description='Saved!', _return=True, color='success')
#                     await msg_output.clear_reactions()
#                     await msg_output.edit(embed=embed)
#
#                     # Set the new panel for selected users
#                     rows = self.db_conn.fetch_table('role_sync')
#                     panel = '**Newly configured roles:**\n'
#                     for row in rows:
#                         panel += f'{row[1]}\n'
#                     new_current = await self.bot.embed_print(ctx, color='info',
#                                                              description=panel,
#                                                              _return=True)
#                     await current_selections.edit(embed=new_current)
#                     return
#
#                 # Get a new panel
#                 block = indexer[str(index)]                 # {'1': (0, 9)}
#                 role_names = roles_list[block[0]:block[1]]  # roles_list[0, 9]
#                 panel = get_panel_embed(role_names, roles_dict, emoji, count=f'{index}/{len(indexer)}')
#                 embed_panel = await self.bot.embed_print(ctx, description=panel, _return=True)
#                 await msg_output.edit(embed=embed_panel)
#
#             except asyncio.TimeoutError:
#                 await msg_output.clear_reactions()


def get_panel_embed(roles_names, roles_dict, emoji, count):
    """Returns the formatted panel to be places inside the embed"""
    panel = ('**Select the roles you want to configure:**\n'
             f'`  ` {emoji["delete"]} `Cancel operation`\n'
             f'`  ` {emoji["save"]} `Save settings and commit`\n'
             f'`  ` {emoji["right"]} `Next page`\n'
             f'`  ` Page: {count}\n\n')
    for idx, role_name in enumerate(roles_names):
        emoji_num = f'rcs{str(idx + 1)}'
        if roles_dict[role_name]['picked']:
            mark = 'checked'
        else:
            mark = 'unchecked'
        panel += f'{emoji[emoji_num]} {emoji[mark]} {role_name}\n'
    return panel


async def set_buttons(ctx, display, emoji):
    """Puts the emojis on the panel"""
    for idx in range(0, 9):
        number = f'rcs{str(idx + 1)}'
        await display.add_reaction(emoji[number])
    await display.add_reaction(emoji['delete'])
    await display.add_reaction(emoji['save'])
    await display.add_reaction(emoji['right'])

def setup(bot):
    bot.add_cog(BotConfigurator(bot))


#cur.execute("INSERT INTO friends(name) VALUES ('Tom')")
        # self.db_conn.cursor.execute("INSERT INTO helpers VALUES (11123,'Jason')")
        # self.db_conn.conn.commit()

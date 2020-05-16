from discord.ext import commands
import logging
import traceback

# Custom
from utils import discord_utils as utils
from utils.discord_arg_parser import arg_parser

class Administrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('root.cogs.administrator')

    async def error_print(self, ctx, title='**Cog Error**', error=None):
        """
        Method is used to consolidate the error outputs since we have to keep
        casting a traceback objects into strings we can just do them here.

        :param ctx:
            Conversation context
        :param title:
            Title to use for the embed
        :param error:
            If string, print the string else convert to a string traceback
        :return:
            None
        """
        if not title.startswith('**C'):
            title = f'**Cog Error:** {title}'

        if not isinstance(error, str):
            error = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))

        self.log.info(error)
        await self.bot.embed_print(ctx, title=title, color='error',
                                   description=error)

    @commands.check(utils.is_owner)
    @commands.command(aliases=['kill'])
    async def _logout(self, ctx):
        self.log.info("Initiating logout phase")
        await self.bot.embed_print(ctx, color='success',
                                   description=f'Closing connection to discord')
        await self.bot.embed_print(
            ctx=self.bot.log_channel,
            description='Connection Closed',
            color='success'
        )
        await self.bot.logout()

    @commands.check(utils.is_owner)
    @commands.command(aliases=['load'])
    async def load_cog(self, ctx, cog: str):
        cog = f'{self.bot.cog_path}{cog}'
        try:
            self.bot.load_extension(cog)

        except commands.errors.ExtensionNotFound:
            await self.error_print(ctx, 'ExtensionNotFound', error=f'Extension `{cog}` was not found')
            return
        except commands.errors.ExtensionFailed as error:
            await self.error_print(ctx, 'ExtensionFailed', error)
            return
        except Exception as error:
            await self.error_print(ctx, error=error)
            return
            
        await self.bot.embed_print(ctx, color='success',
                                   description=f'Loaded `{cog}` successfully')

    @commands.check(utils.is_owner)
    @commands.command(aliases=['unload'])
    async def unload_cog(self, ctx, cog: str):
        cog = f'{self.bot.cog_path}{cog}'
        try:
            self.bot.unload_extension(cog)

        except commands.errors.ExtensionNotFound:
            await self.error_print(ctx, 'ExtensionNotFound', error=f'Extension `{cog}` was not found')
            return
        except commands.errors.ExtensionFailed as error:
            await self.error_print(ctx, 'ExtensionFailed', error)
            return
        except Exception as error:
            await self.error_print(ctx, error=error)
            return

        await self.bot.embed_print(ctx, color='success',
                                   description=f'Unloaded `{cog}` successfully')

    @commands.check(utils.is_owner)
    @commands.command()
    async def re_load(self, ctx, cog: str):
        cog = f'{self.bot.cog_path}{cog}'

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)

        except commands.errors.ExtensionNotFound:
            await self.error_print(ctx, 'ExtensionNotFound', error=f'Extension `{cog}` was not found')
            return
        except commands.errors.ExtensionFailed as error:
            await self.error_print(ctx, 'ExtensionFailed', error)
            return
        except Exception as error:
            await self.error_print(ctx, error=error)
            return

        await self.bot.embed_print(ctx, color='success',
                                   description=f'Reloaded `{cog}` successfully')

    @commands.check(utils.is_owner)
    @commands.command(aliases=['re'])
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
        arg_dict = {
            'run_cmd': {
                'default': None,
                'flags': ['-r', '--run'],
                'switch': False,
                'switch_action': 'False',
                'required': False
            },
            'cmd_args': {
                'default': None,
                'flags': ['-a', '--args'],
                'switch': False,
                'switch_action': 'False',
                'required': False
            }
        }
        parsed_args = await arg_parser(arg_dict, args)
        cog_to_reload = parsed_args['positional']

        # Get the reload object
        reload = self.bot.get_command('re_load')
        await ctx.invoke(reload, cog_to_reload)

        # Optional command to run after reload
        if parsed_args['run_cmd']:
            run_cmd = self.bot.get_command(parsed_args['run_cmd'])
            if run_cmd is None:
                await self.error_print(ctx, 'ExtensionNotFound',
                                       error=f'Extension `{parsed_args["run_cmd"]}` was not found')
                return
            if parsed_args['cmd_args']:
                await ctx.invoke(run_cmd, parsed_args['cmd_args'])
            else:
                await ctx.invoke(run_cmd)

    @commands.check(utils.is_owner)
    @commands.command()
    async def list_cogs(self, ctx):
        print("before")
        self.log.error('%s', ctx)
        print('seven')
        output = ''
        for i in self.bot.cog_tupe:
            output += f"`{i.split('.')[-1]}`\n"
        await self.bot.embed_print(ctx, title='Cog List', description=output)

    @commands.check(utils.is_owner)
    @commands.command()
    async def set_debug(self, ctx, status):
        if status.lower() in ('f', 'false'):
            self.bot.debug = False
            await self.bot.embed_print(ctx, color='success', description='Debugging disabled')
        elif status.lower() in ('t', 'true'):
            self.bot.debug = True
            await self.bot.embed_print(ctx, color='success', description='Debugging enabled')
        else:
            await self.bot.embed_print(ctx, color='error', description='Invalid bool')

    @commands.check(utils.is_owner)
    @commands.command()
    async def emoji_print(self, ctx):
        panel = ''
        for emoji in ctx.guild.emojis:
            print(f'"{emoji.name}": "<:{emoji.name}:{emoji.id}>",')
            if emoji.animated:
                panel += f'<a:{emoji.name}:{emoji.id}> `{emoji.id} | {emoji.name}`\n'
            else:
                panel += f'<:{emoji.name}:{emoji.id}> `{emoji.id} | {emoji.name}`\n'
        await ctx.send(panel)


def setup(bot):
    bot.add_cog(Administrator(bot))

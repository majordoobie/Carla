from argparse import ArgumentParser
import logging
import logging.handlers
import traceback
from pathlib import Path

# Non-built ins
from discord import Embed, Status, Game, InvalidData
from discord.errors import Forbidden
from discord.ext import commands

# Private
from Logging.set_logging import set_logging2
from private.keys.settings import Settings
from private.database.database import BotDatabase

# Global
BOT_LOG = Path('private/logs/carla.log')
DB_LOCATION = 'private/database/carla_db.sqlite'
DESCRIPTION = 'Bot is used to manage discord servers for war planning'
COG_PATH = 'cogs.'
COG_TUPLE = (
    'cogs.admin',
    #'cogs.bot_setup',
)
EMBED_COLORS = {
    'info': 0x000080,       # blue
    'error': 0xff0010,      # red
    'success': 0x00ff00,    # green
    'warning': 0xFFFF00     # yellow
}


class BotClient(commands.Bot):
    def __init__(self, settings, db_conn):
        self.settings = settings
        self.cog_path = COG_PATH
        self.cog_tupe = COG_TUPLE
        self.db_conn = db_conn
        self.log = logging.getLogger('root.CarlaBot')

        # List for storing tracebacks during cog load so we can send to log channel
        self.load_errors = []

        # Objects needed to access server objects. These are loaded after the bot is
        # connected to discord
        self.zbp_server = None
        self.zulu_server = None
        self.log_channel = None

        # This can be set through the bot to enable traceback prints in discord
        self.debug = False

        # This instantiates the bot object into self
        super().__init__(command_prefix=self.settings.bot_config['bot_prefix'])

    def run(self):
        self.log.info('Loading cogs...')
        for extension in COG_TUPLE:
            try:
                self.load_extension(extension)
            except Exception as error:
                # Create a string object out of the traceback
                exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
                self.load_errors.append((extension, exc))
                self.log.error(exc)

        if self.load_errors:
            print('Errors detected, but able to connect. Check logs')
            self.log.info('Errors detected, but able to connect. Check logs')
        else:
            print('Cogs loaded - establishing connection...')

        # Connect bot to discord
        super().run(self.settings.bot_config['bot_token'], reconnect=True)

    async def on_resumed(self):
        self.log.info('Resumed connection from lost connection')
        await self.embed_print(
            ctx=self.log_channel,
            description='Resumed connection from lost connection',
            color='warning'
        )

    async def on_ready(self):
        # Setting up guild objects
        self.zbp_server = self.get_guild(self.settings.zbp_server)
        self.zulu_server = self.get_guild(self.settings.zulu_server)
        self.log_channel = self.zbp_server.get_channel(self.settings.carla_log)

        # Set logging
        #logging.getLogger("chardet.charsetprober").disabled = True
        #self.log = await set_logging(self.log_channel)
        #self.log = await set_logging2(self.log_channel)
        from Logging import setup_logging
        from Logging.setup_logging import BotLogger
        #self.log = await setup_logging.setup()
        self.log = BotLogger(webhook_url=self.settings.webhook_url,
                             file_path="private/logs/carla.log").logger

        self.log.error("Testing queue pipe logging")
        #self.log = set_logging3(self.log_channel)

        # Change presence to version number
        await self.change_presence(status=Status.online, activity=Game(name=self.settings.bot_config['version']))

        # Print load cog errors to channel
        if self.load_errors:
            for k, v in self.load_errors:
                self.log.error(v)
                await self.embed_print(
                    ctx=self.log_channel,
                    title=f'**Cog Load Error:** {k}',
                    description=v,
                    color='warning'
                )

        self.log.info('Bot is connected')
        print('Bot is connected')
        await self.embed_print(
            ctx=self.log_channel,
            description='Connection established',
            color='success'
        )

    async def on_command(self, ctx):
        await ctx.message.channel.trigger_typing()

    async def on_command_error(self, ctx, error):
        if self.debug:
            exc = ''.join(
                traceback.format_exception(type(error), error, error.__traceback__, chain=True))

            await self.embed_print(ctx, title='DEBUG ENABLED', description=f'{exc}',
                                   codeblock=True, color='warning')

        # Catch all errors within command logic
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            # Catch errors such as roles not found
            if isinstance(original, InvalidData):
                await self.embed_print(ctx, title='INVALID OPERATION', color='error',
                                       description=original.args[0])
                return

            # Catch permission issues
            elif isinstance(original, Forbidden):
                await self.embed_print(ctx, title='FORBIDDEN', color='error',
                                       description='Even with proper permissions, the target user must be lower in the '
                                       'role hierarchy of this bot.')
                return

        # Catch command.Check errors
        if isinstance(error, commands.CheckFailure):
            try:
                if error.args[0] == 'Not owner':
                    await self.embed_print(ctx, title='COMMAND FORBIDDEN', color='error',
                                           description='Only Doobie can run this command')
                    return
            except:
                pass
            await self.embed_print(ctx, title='COMMAND FORBIDDEN', color='error',
                                   description='Only `CoC Leadership` are permitted to use this command')
            return

        # Catch all
        await self.embed_print(ctx, title='COMMAND ERROR',
                               description=str(error), color='error')

    async def embed_print(self, ctx, title='', description=None, color='info', codeblock=False, _return=False):
        """
        Method used to standardized how stuff is printed to the users
        Parameters
        ----------
        ctx
        title
        description
        color

        Returns
        -------
        """
        if len(description) < 1000:
            if codeblock:
                description = f'```{description}```'
            embed = Embed(
                title=f'{title}',
                description=description,
                color=EMBED_COLORS[color]
            )
            embed.set_footer(text=self.settings.bot_config['version'])
            if _return:
                return embed
            await ctx.send(embed=embed)
        else:
            blocks = await self.text_splitter(description, codeblock)
            embed_list = []
            embed_list.append(Embed(
                title=f'{title}',
                description=blocks[0],
                color=EMBED_COLORS[color]
            ))
            for i in blocks[1:]:
                embed_list.append(Embed(
                    description=i,
                    color=EMBED_COLORS[color]
                ))
            embed_list[-1].set_footer(text=self.settings.bot_config['version'])
            if _return:
                return embed_list

            for i in embed_list:
                await ctx.send(embed=i)

    async def text_splitter(self, text, codeblock):
        '''
        Method is used to split text by 1000 character increments to avoid hitting the
        1400 character limit on discord
        '''
        blocks = []
        block = ''
        for i in text.split('\n'):
            if (len(i) + len(block)) > 1000:
                block = block.rstrip('\n')
                if codeblock:
                    blocks.append(f'```{block}```')
                else:
                    blocks.append(block)
                block = f'{i}\n'
            else:
                block += f'{i}\n'
        if block:
            if codeblock:
                blocks.append(f'```{block}```')
            else:
                blocks.append(block)
        return blocks


class BotArgs(ArgumentParser):
    """Makes sure the right arguments are used when starting the bot"""
    def __init__(self):
        super().__init__(description=DESCRIPTION)
        self.group = self.add_mutually_exclusive_group(required=True)
        self.group.add_argument('--live', help='Run bot in Carla shell',
                                action='store_true', dest='live_mode')

        self.group.add_argument('--dev', help='Run bot in devShell shell',
                                action='store_true', dest='dev_mode')

    def parse_the_args(self):
        return self.parse_args()


def setup_logging():
    log = logging.getLogger('root')
    log.setLevel(logging.DEBUG)
    log_handler = logging.handlers.RotatingFileHandler(
        BOT_LOG,
        encoding='utf-8',
        maxBytes=100000000,
        backupCount=2
    )
    log_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('''\
[%(asctime)s]:[%(levelname)s]:[%(name)s]:[Line:%(lineno)d][Func:%(funcName)s]
[Path:%(pathname)s]
MSG: %(message)s
''', "%d %b %H:%M:%S")
    log_handler.setFormatter(formatter)
    log.addHandler(log_handler)
    log.info('Logger initialized')
    return log


def main(bot_mode):
    """Starts the bot"""
    #log = setup_logging()
    db_conn = None
    try:
        db_conn = BotDatabase(DB_LOCATION)
        settings = Settings(bot_mode)
        bot = BotClient(settings=settings, db_conn=db_conn)
        bot.run()

    except Exception as error:
        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        print(exc)
        #log.error(exc)

    finally:
        if db_conn:
            print("closing db")
            db_conn.close_db()



if __name__ == '__main__':
    args = BotArgs().parse_the_args()
    if args.live_mode:
        main('live_mode')
    else:
        main('dev_mode')

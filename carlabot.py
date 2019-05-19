import discord
import logging
from discord.ext import commands
import sys, traceback
import json

# load settings
with open("Configuration/settings.json") as jfile:
    settings = json.load(jfile)

# tuple of the cogs to load
dah_cogs = (
    "cogs.test"
    )

# Instanciate the bot
bot = commands.Bot(command_prefix="/", description="Testing yoooo")

def setup_logging():
    """ Shamelessly stripped from DannyBot """
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='carlabot.log', encoding='utf-8', mode='w')
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

def main():
    """ Load Cogs """
    bot.run(settings["devMode"]["bot_config"]["bot_token"])
    for cog in dah_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f"Failed to load extention {cog}", file=sys.stderr)

@bot.event
async def on_ready():
    print("Logged on bitch")



    
if __name__ == "__main__":
    main()
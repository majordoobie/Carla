import asyncio

import aiohttp
from discord import Webhook, RequestsWebhookAdapter, Embed

# Logging modules
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

# Format for logs
DEFAULT_FORMAT = ('''\
[%(asctime)s]:[%(levelname)s]:[%(name)s]:[Line:%(lineno)d][Func:%(funcName)s]
[Path:%(pathname)s]
MSG: %(message)s
''')

class DiscordWebhookHandler(logging.Handler):
    def __init__(self, webhook_url=None):
        super().__init__()
        self.webhook_url = webhook_url

        if not self.webhook_url:
            raise AttributeError("No webhook url specified for webhook log.")

    def emit(self, record):
        try:
            self.discord_log(record)
        except Exception:
            self.handleError(record)

    def discord_log(self, record):
        webhook = Webhook.from_url(self.webhook_url, adapter=RequestsWebhookAdapter())
        color = self.get_color(record.levelname)
        embed = Embed(title='Error',
                      description=record.msg,
                      color=color)
        #embed.set_footer(record.name)
        print(record.levelname)
        print(record.msg)
        print('Logger name: ' + record.name)
        webhook.send(embed=embed, username='Carla Logger Webhook')

    def get_color(self, levelname):
        colors = {
            'ERROR' : 0xFF0000,
            'WARNING' : 0xFFFF00,
            'INFO' : 0x00FF00,
            'DEBUG' : 0x9933FF
        }
        return colors[levelname]


class BotLogger:
    def __init__(self, webhook_log=True, webhook_url=None, file_log=True, file_path=None):
        # List of handlers
        self.log_handlers = []
        self.logger = None
        self.queue_listener = None
        self.log_queue = Queue(-1)

        # Check if webhook logging is enabled
        if webhook_log:
            if not webhook_url:
                raise AttributeError("No webhook url specified for webhook log.")
            else:
                self.webhook_url = webhook_url
                discord_handler = DiscordWebhookHandler(self.webhook_url)
                discord_handler.setLevel(logging.DEBUG)
                self.log_handlers.append(discord_handler)
                #self.log_handlers.append(DiscordWebhookHandler(self.webhook_url))


        # Check if log file logging is enabled
        if file_log:
            if not file_path:
                raise AttributeError("No filepath specified for file log.")
            else:
                self.file_path = file_path
                file_handler = self.get_file_handler()
                file_handler.setLevel(logging.DEBUG)
                self.log_handlers.append(file_handler)
                #self.log_handlers.append(self.get_file_handler().setLevel(logging.DEBUG))

        if self.log_handlers:
            self.set_queue_handler()
            self.set_queue_logger()
            self.queue_listener.start()

    def set_queue_handler(self):
        # Create queue
        queue_handler = QueueHandler(self.log_queue)
        logger = logging.getLogger('root')
        logger.setLevel(logging.DEBUG) # Enable all and let handlers deal with dialing in
        logger.addHandler(queue_handler)
        self.logger = logger

    def set_queue_logger(self):
        self.queue_listener = QueueListener(self.log_queue,
                                            *self.log_handlers,
                                            respect_handler_level=True)

    def get_file_handler(self):
        """
        Return a rotating log handler
        """
        _logger_handler = logging.handlers.RotatingFileHandler(
            self.file_path,
            encoding='utf-8',
            maxBytes=100000000,
            backupCount=2
        )
        formatter = logging.Formatter(DEFAULT_FORMAT, "%d %b %H:%M:%S")
        _logger_handler.setFormatter(formatter)
        return _logger_handler







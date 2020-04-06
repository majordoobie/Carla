import asyncio

import aiohttp
from discord import Webhook, AsyncWebhookAdapter, RequestsWebhookAdapter, Embed

# Logging modules
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from pathlib import Path

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
        embed = Embed(title='Error', description='Hellow')
        webhook.send(embed=embed, username='Foo')


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
                self.log_handlers.append(DiscordWebhookHandler(self.webhook_url))

        # Check if log file logging is enabled
        if file_log:
            if not file_path:
                raise AttributeError("No filepath specified for file log.")
            else:
                self.file_path = file_path
                self.log_handlers.append(self.get_file_handler())

        if self.log_handlers:
            self.set_queue_handler()
            self.set_queue_logger()
            self.queue_listener.start()

    def set_queue_handler(self):
        # Create queue
        queue_handler = QueueHandler(self.log_queue)
        logger = logging.getLogger()
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
        _logger_handler.setLevel(logging.INFO)
        return _logger_handler

#
# async def setup():
#     # Create queue
#     log_queue = Queue(-1)
#
#     # Give queue handler the queue created
#     queue_handler = QueueHandler(log_queue)
#
#     # Get all the other handlers you need
#     stdout_handler = logging.StreamHandler()
#     discord_handler = DiscordWebhookHandler(
#                                             )
#
#     # Set up the queue listener to listen of the all registered handlers
#     queue_listener = QueueListener(log_queue, discord_handler)
#
#     # Get the main logger and set up the queue handler to it
#     logger = logging.getLogger()
#     logger.addHandler(queue_handler)
#
#
#     queue_listener.start()
#     logger.debug("Is this working")
#     return logger






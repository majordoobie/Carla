from atexit import register
import logging
from pathlib import Path
from queue import Queue
from logging.handlers import QueueHandler, QueueListener


BOT_LOG = Path('private/logs/carla.log')
DEFAULT_FORMAT = ('''\
[%(asctime)s]:[%(levelname)s]:[%(name)s]:[Line:%(lineno)d][Func:%(funcName)s]
[Path:%(pathname)s]
MSG: %(message)s
''')
# class DiscordHandler(Handler):
#     def emit(self, record):
#         log_entry = self.format(record)
#         return requests.post('http://example.com:8080/',
#                              log_entry, headers={"Content-type": "application/json"}).content


class DiscordQueueLogger(QueueHandler):
    def __init__(self, handlers, respect_handlers=True, auto_run=True):
        queue = Queue(-1)
        super().__init__(queue)
        self._listener = QueueListener(
            self.queue,
            *handlers,
            respect_handler_level=respect_handlers)
        if auto_run:
            self.start()
            # Register this function before the application closes
            register(self.stop)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def emit(self, record):
        return super().emit(record)


def get_file_handler():
    _logger_handler = logging.handlers.RotatingFileHandler(
        BOT_LOG,
        encoding='utf-8',
        maxBytes=100000000,
        backupCount=2
    )
    formatter = logging.Formatter(DEFAULT_FORMAT, "%d %b %H:%M:%S")
    _logger_handler.setFormatter(formatter)
    _logger_handler.setLevel(logging.INFO)
    return _logger_handler

def get_discord_handler(channel)

async def set_logging(channel):
   # await channel.send('Test')
    # Get root logger
    log = logging.getLogger('root')
    log.setLevel(logging.DEBUG)

    # Create rotating file handler
    rotating_log_handler = get_file_handler()

    # Add loggers
    log.addHandler(rotating_log_handler)

    # Debug that it is running
    log.debug('Logger initialized')
    return log

def set_logging2(channel):
    # Create the queue that will connect the app thread and log thread
    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)

    # Get the root logger and add the queue handler to it
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(queue_handler)

    # Create rotating file handler
    rotating_log_handler = get_file_handler()
    queue_listener = QueueListener(log_queue, rotating_log_handler, respect_handler_level=True)
    queue_listener.start()
    logger.debug("We are in with wueue")
    return logger

async def set_logging3(channel):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    rotating_log_handler = get_file_handler()
    discord_channel_handler = get_discord_handler(channel)

    logger.addHandler(DiscordQueueLogger([rotating_log_handler]))
    logger.debug('debug test')
    logger.info('info test')
    logger.critical('critical test')

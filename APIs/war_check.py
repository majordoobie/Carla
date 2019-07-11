import threading
import queue
import logging
from time import sleep

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
HDNL = logging.FileHandler(filename='war_cycle.log', encoding='utf-8', mode='a+')
HDNL.setFormatter(logging.Formatter('[%(asctime)s]:[%(levelname)s]:[%(name)s]:[Line:%(lineno)d][Fun'
                                    'c:%(funcName)s]\n[Path:%(pathname)s]\n MSG: %(message)s\n',
                                    "%d %b %H:%M:%S"))
LOG.addHandler(HDNL)


class MyThread(threading.Thread):
    def __init__(self, name, wait_time):
        threading.Thread.__init__(self)
        self.name = name
        self.wait_time = wait_time

    def run(self):
        LOG.info(f'Starting thread {self.name}')
        process_thread(self.wait_time)
        LOG.info(f'Stopped thread {self.name}')


class War_Check():
    def __init__(self, discord_client, config, coc_client):
        self.bot = discord_client
        self.config = config
        self.coc_client = coc_client
        self._queue = queue.Queue()
        
        # Need to be joined
        self.z_join = False

        # In timer sequence
        self.m_timer = False
        self.z_timer = False
        self.e_timer = False

    async def run(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            # set variables to false
            z_thread, m_thread, e_thread = False,False,False

            threads = []
            # check for the timers
            if self.z_timer == False:
                result = await self.coc_client.get_current_war("#2Y28CGP8")
                if result.state == "preparation":
                    self.z_timer = True
                    self.z_join = True
                    z_thread = MyThread("Zulu_thread", result.end_time.seconds_until)
                    threads.append(z_thread)

            if self.m_timer == False:
                result = await self.coc_client.get_current_war("#P0Q8VRC8")
                print(f"Misfits status {result.state}")
                if result.state == "preparation":
                    self.m_timer = True
                    self.m_join = True
                    m_thread = MyThread("Misfits_thread", result.end_time.seconds_until)
                    threads.append(m_thread)

            if self.e_timer == False:
                result = await self.coc_client.get_current_war("#8YGOCQRY")
                print(f"Elephino status {result.state}")
                if result.state == "preparation":
                    self.e_timer = True
                    self.e_join = True
                    e_thread = MyThread("Elephino_thread", result.end_time.seconds_until)
                    threads.append(e_thread)

            for thread in threads:
                thread.start()
            for thread in threads:
                if thread.name == "Zulu_thread":
                    self.z_join = False
                    self.z_timer = False
                elif thread.name == "Misfits_thread":
                    self.m_join = False
                    self.m_timer = False
                elif thread.name == "Elephino_thread":
                    self.e_join = False
                    self.e_timer = False
                thread.join()

def process_thread(wait_time):
    print(wait_time)
    sleep(10)

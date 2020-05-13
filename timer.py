import os
import signal
import time
import threading
import logging
from constants import logger_name


def kill(pid: int):
    try:
        return os.kill(pid, signal.SIGKILL)
    except ProcessLookupError as err:
        pass


class Timer(threading.Thread):
    def __init__(self, pid, timeout):
        super().__init__()
        self._start_time = time.time()
        self._expect_end = self._start_time + (timeout / 1000)
        self.pid = pid
        self.timeout = timeout
        self.logger = logging.getLogger(logger_name)
        self.stop_event = threading.Event()

    def run(self):
        try:
            while not self.stop_event.is_set() and time.time() < self._expect_end:
                time.sleep(0.001)
        except OSError as e:
            self.logger.error('Run timer failed: ' + e.__str__())
        finally:
            if time.time() > self._expect_end:
                self.logger.debug('Real time exceeded, killing process')
                kill(self.pid)

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()
import time
import sys
import signal
import os

import logging

from iot_utils.exceptions import UnrecoverableError


class ProcessRunner():
    GRACEFULL_STOP = False
    _INIT = False

    def __init__(self,
            cls,
            loop_intrvl: int,
            loglev: str = "INFO"
        ):
        self.LOOP_INTERVAL = loop_intrvl

        if not ProcessRunner._INIT:

            loglev = logging.getLevelName(os.getenv("LOGGING_LOG_LEV", loglev))

            logging.basicConfig(level=loglev, stream=sys.stdout,
                format= "[%(levelname)7s %(asctime)s] %(name)s: %(message)s", datefmt="%d%b%Y %H:%M:%S"
            )

            signal.signal(signal.SIGTERM, ProcessRunner.kill_handler)
            signal.signal(signal.SIGINT, ProcessRunner.gracefull_handler)

            ProcessRunner._INIT = True

        self.cls = cls

    @staticmethod
    def kill_handler(signal_received, frame):
        logging.info('SIGTERM detected. Exiting ...')
        sys.exit(0)

    @staticmethod
    def gracefull_handler(signal_received, frame):
        logging.info('SIGINT or CTRL-C detected. Exiting gracefully')
        ProcessRunner.GRACEFULL_STOP = True

    def main(self):
        while True:
            try:
                ctrl = self.cls()
                while True:
                    ctrl.loop()
                    if ProcessRunner.GRACEFULL_STOP:
                        if hasattr(ctrl, "shutdown"):
                            ctrl.shutdown()
                        break
                    time.sleep( self.LOOP_INTERVAL )
            except UnrecoverableError:
                logging.error("*** Unrecoverable error. Please check the log. Cannot proceed. ***")
                sys.exit(1)
            except Exception as e:
                logging.error(f"Error during execution loop: {e}")
                logging.info("Trying to resume after 10 secs ...")
                time.sleep(10)
            if ProcessRunner.GRACEFULL_STOP:
                break


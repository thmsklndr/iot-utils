import time
import sys
import signal
import os

import logging
from typing import Type

from iot_utils.exceptions import UnrecoverableError

_dflt_log_lev = os.getenv("LOGGING_LOG_LEV", "WARN")

class ProcessRunner:
    GRACEFULL_STOP = False
    _INIT = False

    def __init__(self,
            cls: Type,
            loop_intrvl: int,
            logger: logging.Logger = logging.root,
            sys_loglev: str = _dflt_log_lev,
            sys_log_fmt: str = "[%(levelname)7s %(asctime)s] %(name)s: %(message)s",
            sys_log_datefmt: str = "%d%b%Y %H:%M:%S"
        ):
        self.LOOP_INTERVAL = loop_intrvl
        self.logger = logger

        if not ProcessRunner._INIT:

            loglev = logging.getLevelName(sys_loglev)

            logging.basicConfig(level=loglev, stream=sys.stdout,
                format= sys_log_fmt, datefmt=sys_log_datefmt
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
        msg_flag = True
        while True:
            try:
                ctrl = self.cls()
                while True:
                    ctrl.loop()
                    msg_flag = True
                    if ProcessRunner.GRACEFULL_STOP:
                        if hasattr(ctrl, "shutdown"):
                            ctrl.shutdown()
                        break
                    time.sleep( self.LOOP_INTERVAL )
            except UnrecoverableError:
                self.logger.error("*** Unrecoverable error. Please check the log. Cannot proceed. ***")
                break
            except Exception as e:
                if msg_flag:
                    self.logger.error(f"Error during execution loop: {e}")
                    msg_flag = False

                time.sleep(10)

            if ProcessRunner.GRACEFULL_STOP:
                break


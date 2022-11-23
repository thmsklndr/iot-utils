import time

import gps
import threading

import logging
logger = logging.getLogger('gps.ifc')

# see https://gpsd.gitlab.io/gpsd/gpsd_json.html#_tpv
mode_states = {
    0: "unknown",
    1: "no fix",
    2: "2D",
    3: "3D"
}
status_states = {
    0: "Unknown",
    1:  "Normal",
    2:  "DGPS",
    3:  "RTK Fixed",
    4:  "RTK Floating",
    5:  "DR",
    6:  "GNSSDR",
    7:  "Time (surveyed)",
    8:  "Simulated",
    9:  "P(Y)"
}

class GPS_ifc(threading.Thread):

    def __init__(self, gpsd_host: str = "gpsd"):
        super().__init__()
        logger.info(f"Initializting gpsd: {gpsd_host}.")
        self.gpsd = gps.gps(host=gpsd_host, mode=gps.WATCH_ENABLE) #|gps.WATCH_NEWSTYLE)
        self.running = True #setting the thread running to true

        self._state = True

    @property
    def state(self) -> bool:
        return self._state

    def run(self) -> None:
        error_cnt = 0
        missing_data_cnt = 0
        while self.running:
            try:
                data = self.gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
                #logger.debug(data)

                if data == 0:
                    error_cnt += 1
                else:
                    # resetting error cnts if next() did not throw
                    error_cnt = 0
                    missing_data_cnt = 0
            except StopIteration as se:
                self._state = False
                self.running = False
            except KeyError:
                missing_data_cnt += 1
                logger.warning(f"Missing data from gpsd ({missing_data_cnt})")
            except Exception as e:
                error_cnt += 1
                logger.exception(e)

            # if we could not get data for ten times we stop running and need to take action
            # state property will be false
            if error_cnt > 10:
                self._state = False
                self.running = False

        self.gpsd.close()

    def get_gps_data(self) -> dict:

        ret = {}

        if self.state:
            try:
                fix: gps.gpsfix = self.gpsd.fix
                if fix.status:
                    lat = fix.latitude
                    long = fix.longitude

                    if gps.isfinite(fix.latitude) and gps.isfinite(fix.longitude):
                        ret = {
                            "latitude": fix.latitude,
                            "longitude": fix.longitude,
                            "mode": mode_states[fix.mode],
                            "status": status_states[fix.status],
                            "error_long": fix.epx,
                            "error_lat": fix.epy,
                            "error_vertical": fix.epv,
                            "speed": fix.speed,
                            "uSat": self.gpsd.satellites_used,
                            "nSat": len(self.gpsd.satellites),
                            "timestamp": time.time()
                        }

                # nx = self.gpsd.next()
                # logger.debug(nx)
                # # For a list of all supported classes and fields refer to:
                # # https://gpsd.gitlab.io/gpsd/gpsd_json.html
                # if nx['class'] == 'TPV':
                #     ret = {
                #             "latDG": getattr(nx,'lat'),
                #             "longDG": getattr(nx,'lon')
                #     }
                # elif nx['class'] == 'SKY':
                #     logger.info(f"Satellites (used/found): {getattr(nx,'uSat', -1)}/{getattr(nx,'nSat', -1)}")
            except Exception as e:
                logging.error(f"Failed to get GPS position: {e}")

        return ret


import json
import logging
import shutil

logger = logging.getLogger("iot_utils.sys")

def get_sys_temperature():
    retval = "N/A"
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read().rstrip()) / 1000
            retval = f"{round(temp,1)}"
    except:
        try:
            # 2nd try: using psutils
            import psutil
            sens = psutil.sensors_temperatures()
            for v in sens.values():
                for i in v:
                    if i.label == "Tdie":
                        retval = f"{round(i.current, 1)}"
                        break
        except Exception as e:
            logger.exception("Error occurred. Unable to get temp from psutils")
    return retval

async def async_get_sys_temperature():
    return get_sys_temperature()

def get_fs_usage(fs:str = '/'):
    total, used, free = ( 'n/a', 'n/a', 'n/a' )
    try:
        total, used, free = shutil.disk_usage(fs)
    except Exception:
        logger.exception(f"Error occurred. Unable to get size for '{fs}'")

    return {
        'total': total,
        'used': used,
        'free': free
    }
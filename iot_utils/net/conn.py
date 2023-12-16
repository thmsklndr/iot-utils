
import socket
import time

import logging
logger = logging.getLogger("iot_utils.net")

def check_open_port(address: str, port: int, wait_t: float = None):
    # Create a TCP socket
    ret = False
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        if sock.connect_ex((address, port)) == 0:
            ret = True
    except socket.error:
        pass
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            if wait_t:
                time.sleep(wait_t)
        except:
            logger.error(f"Failed to close socket {address}:{port}")

    return ret

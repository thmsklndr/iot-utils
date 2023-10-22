# see https://gist.github.com/FulcronZ/9948756fea515e6d18b8bc2c7182bdb8
import json
import logging
import time

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

class MQTTHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a MQTT server to a topic.
    """
    def __init__(self, hostname, topic, qos=0, retain=False,
            port=1883, client_id='', keepalive=60, will=None, auth=None,
            tls=None, protocol=mqtt.MQTTv31, transport='tcp'):
        logging.Handler.__init__(self)
        self.topic = topic
        self.qos = qos
        self.retain = retain
        self.hostname = hostname
        self.port = port
        self.client_id = client_id
        self.keepalive = keepalive
        self.will = will
        self.auth = auth
        self.tls = tls
        self.protocol = protocol
        self.transport = transport

    def emit(self, record):
        """
        Publish a single formatted logging record to a broker, then disconnect
        cleanly.
        """
        payload = {
            "msg": record.msg,
            "timestamp": time.time(),
            "log_lev": record.levelname,
            "module_name": record.name
        }

        msg = json.dumps(payload)

        publish.single(self.topic, msg, self.qos, self.retain,
            hostname=self.hostname, port=self.port,
            client_id=self.client_id, keepalive=self.keepalive,
            will=self.will, auth=self.auth, tls=self.tls,
            protocol=self.protocol, transport=self.transport)


def getMQTTLogger(name: str,
                  mqtt_host: str,
                  mqtt_topic: str,
                  level,
                  fmt="[%(asctime)s] %(name)s: %(message)s",
                  datefmt="%d%b%Y %H:%M:%S"
                  ):
    logger = logging.getLogger(name)
    handler = MQTTHandler(mqtt_host, mqtt_topic)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(fmt=fmt, datefmt=datefmt)
    )
    logger.addHandler(handler)
    return logger


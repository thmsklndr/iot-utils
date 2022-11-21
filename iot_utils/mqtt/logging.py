# see https://gist.github.com/FulcronZ/9948756fea515e6d18b8bc2c7182bdb8

import logging
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
        msg = self.format(record)
        publish.single(self.topic, msg, self.qos, self.retain,
            hostname=self.hostname, port=self.port,
            client_id=self.client_id, keepalive=self.keepalive,
            will=self.will, auth=self.auth, tls=self.tls,
            protocol=self.protocol, transport=self.transport)

# hostname = 'iot.eclipse.org'
# topic = 'orgID/appName/clusterID/deviceID/'
#
# # Create and configure a logger instance
# logger = logging.getLogger('')
# myHandler = MQTTHandler(hostname, topic)
# myHandler.setLevel(logging.INFO)
# myHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
# logger.addHandler(myHandler)

import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger("iot_utils.mqtt")

class MQTT_client:
    def __init__(self, mqtt_name):
        self.client = mqtt.Client()
        self.name = mqtt_name

    def __enter__(self):
        logger.debug("Entering mqtt client context")
        ret = self.client.connect(self.name, 1883, 60)
        if ret != 0:
            raise RuntimeError("Failed to connect to internal mqtt server")
        return self.client

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.disconnect()
        logger.debug("Leaving mqtt client context")


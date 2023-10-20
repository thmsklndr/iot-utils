import json
import os
import time
from pathlib import Path
from pprint import pformat
from typing import Callable

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from dotenv import load_dotenv

#load_dotenv("/app/.env")
#load_dotenv(".env")

import logging
logger = logging.getLogger('aws_ifc')


class AWS_client:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def connect(self):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)

        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        kwargs = {
                    "port"             : 8883,
                    "clean_session"    : False,
                    "client_bootstrap" : client_bootstrap,
                    "keep_alive_secs"  : 6
        }
        kwargs.update(self.kwargs)

        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(**kwargs)

        logger.debug("Connecting to AWS IOT with the following parameters:")
        logger.debug(pformat(self.kwargs))

        connect_future = self.mqtt_connection.connect()
        connect_future.result()

        logger.debug("Successfully connected ...")
        return self.mqtt_connection


    def disconnect(self):
        logger.debug("cleaning up aws client ...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()

# https://aws.amazon.com/de/premiumsupport/knowledge-center/iot-core-publish-mqtt-messages-python/
# https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/cognito_connect.py
# https://docs.aws.amazon.com/iot/latest/developerguide/sdk-tutorials.html
'''
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint         =ENDPOINT,
            cert_filepath    =PATH_TO_CERTIFICATE,
            pri_key_filepath =PATH_TO_PRIVATE_KEY,
            client_bootstrap =client_bootstrap,
            ca_filepath      =PATH_TO_AMAZON_ROOT_CA_1,
            client_id        =CLIENT_ID,
            clean_session    =False,
            keep_alive_secs  =6
            )
'''

_dflt_client_id = os.getenv("AWS_CLIENT_ID", None )

class AWS_iot:
    def __init__(self) -> None:

        self.client_id         = os.getenv("AWS_CLIENT_ID")
        self.topic_data        = os.getenv("AWS_TOPIC_DATA")
        self.topic_status      = os.getenv("AWS_TOPIC_STATUS")
        self.endpoint          = os.getenv("AWS_IOT_ENDPOINT")

        #cert_path              = Path(os.getenv("CERTS_PATH", "/certs/" ))
        cert_path              = Path( "/certs/" )

        self.ca_filepath       = cert_path / os.getenv("AWS_CA_FILE",       "AmazonRootCA1.pem")
        self.cert_filepath     = cert_path / os.getenv("AWS_CERT_FILE",     "certificate.pem.crt")
        self.priv_key_filepath = cert_path / os.getenv("AWS_PRIV_KEY_FILE", "private.pem.key")

        for cfile in (self.ca_filepath, self.cert_filepath, self.priv_key_filepath):
            if not cfile.exists():
                raise FileNotFoundError(f"Required file not found: {cfile}")

        self._client = None

    @property
    def client(self):
        if self._client is None: # or invalid

            self._client = AWS_client(
                    client_id=self.client_id,
                    endpoint=self.endpoint,
                    cert_filepath=self.cert_filepath.as_posix(),
                    pri_key_filepath=self.priv_key_filepath.as_posix(),
                    ca_filepath=self.ca_filepath.as_posix()

            )
            self._client.connect()
        return self._client.mqtt_connection

    def publish(self, topic, payload) -> None:

            logger.debug('Begin Publish')


            _p_json = json.dumps( { "timestamp": time.time(), "payload": payload } )

            self.client.publish(topic = topic, payload = _p_json, qos = mqtt.QoS.AT_LEAST_ONCE )

            logger.debug(f"Published data to topic: {topic}")
            logger.debug(f"{_p_json}")
            logger.debug('Publish End')

    def publish_data(self, payload):
        self.publish(self.topic_data, payload)

    def publish_status(self, payload):
        self.publish(self.topic_status, payload)

    def subscribe(self, topic: str, callback: Callable):
        subscribe_future, packet_id = self.client.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=callback
        )
        subscribe_result = subscribe_future.result()
        return subscribe_result


if __name__ == '__main__':
    from datetime import datetime
    aws_ifc = AWS_iot()
    dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    aws_ifc.publish_status(f"Logging: connection established for client sample @{dt}.")

    message_topic = 'live_inventory/status'
    TIMEOUT = 100

    def sub_handler(topic, payload, **kwargs):
        print("Received message from topic '{}': {}".format(topic, payload))

    aws_ifc.subscribe(message_topic, sub_handler)

    while True:
        time.sleep(5)
    # print("Subscribing to topic '{}'...".format(message_topic))
    # subscribe_future = client.subscribe(subscribe_packet=mqtt5.SubscribePacket(
    #     subscriptions=[mqtt5.Subscription(
    #         topic_filter=message_topic,
    #         qos=mqtt5.QoS.AT_LEAST_ONCE)]
    # ))
    # suback = subscribe_future.result(TIMEOUT)
    # print("Subscribed with {}".format(suback.reason_codes))
    #
    # # Publish message to server desired number of times.
    # # This step is skipped if message is blank.
    # # This step loops forever if count was set to 0.
    # if message_string:
    #     if message_count == 0:
    #         print("Sending messages until program killed")
    #     else:
    #         print("Sending {} message(s)".format(message_count))
    #
    #     publish_count = 1
    #     while (publish_count <= message_count) or (message_count == 0):
    #         message = "{} [{}]".format(message_string, publish_count)
    #         print("Publishing message to topic '{}': {}".format(message_topic, message))
    #         publish_future = client.publish(mqtt5.PublishPacket(
    #             topic=message_topic,
    #             payload=json.dumps(message_string),
    #             qos=mqtt5.QoS.AT_LEAST_ONCE
    #         ))
    #
    #         publish_completion_data = publish_future.result(TIMEOUT)
    #         print("PubAck received with {}".format(repr(publish_completion_data.puback.reason_code)))
    #         time.sleep(1)
    #         publish_count += 1
    #
    # received_all_event.wait(TIMEOUT)
    # print("{} message(s) received.".format(received_count))

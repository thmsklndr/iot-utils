from pprint import pformat
import os
from pathlib import Path
import time
import json

from awscrt import io, mqtt
from awscrt.exceptions import AwsCrtError
from awsiot import mqtt_connection_builder

from dotenv import load_dotenv
load_dotenv("/app/.env")

import logging
logger = logging.getLogger('aws_ifc')

from iot_utils.proc import UnrecoverableError

class AWS_client:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        try:
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

            logger.info("Connecting to AWS IOT with the following parameters:")
            logger.info(pformat(self.kwargs))

            connect_future = self.mqtt_connection.connect()
            connect_future.result()

            logger.info("Successfully connected ...")
            return self.mqtt_connection
        except AwsCrtError as e:
            logger.error("Could not connect to AWS IOT: Please check the certificates !!!")
            raise UnrecoverableError()


    def __exit__(self, exc_type, exc_value, exc_traceback):
        logger.info("cleaning up aws client ...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()

# https://aws.amazon.com/de/premiumsupport/knowledge-center/iot-core-publish-mqtt-messages-python/
#
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

    def _publish(self, topic, payload) -> None:
        with AWS_client(

                    client_id        = self.client_id,
                    endpoint         = self.endpoint,
                    cert_filepath    = self.cert_filepath.as_posix(),
                    pri_key_filepath = self.priv_key_filepath.as_posix(),
                    ca_filepath      = self.ca_filepath.as_posix()
            
            ) as client:

            logger.info('Begin Publish')


            _p_json = json.dumps( { "timestamp": time.time(), "payload": payload } )

            client.publish(topic = topic, payload = _p_json, qos = mqtt.QoS.AT_LEAST_ONCE )

            logger.info(f"Published data to topic: {topic}")
            logger.info(f"{_p_json}")
            logger.info('Publish End')

    def publish_data(self, payload):
        self._publish(self.topic_data, payload)

    def publish_status(self, payload):
        self._publish(self.topic_status, payload)


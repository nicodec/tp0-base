import logging
import socket

from infrastructure.client.client_config import ClientConfig
from infrastructure.common.socket_utils import send_message, recv_message
from infrastructure.common.message import Message, ErrorCode

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.socket = None

    def connect_to_server(self):
        """Establishes a TCP connection with the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_data = self.config.server_address.split(':')
            self.socket.connect((server_data[0], int(server_data[1])))
            logger.debug(
                f"Client {self.config.id} successfully connected to {self.config.server_address}")
            return True
        except Exception as e:
            logger.debug(f"Connection error: {str(e)}")
            return False

    def disconnect_from_server(self):
        """Closes the TCP connection with the server"""
        if self.socket:
            try:
                self.socket.close()
                logger.debug(
                    f"Client {self.config.id} successfully disconnected")
            except Exception as e:
                logger.debug(f"Disconnection error: {str(e)}")
        self.socket = None


    def send_data(self, data):
        """Sends data to the server and waits for a response"""
        try:
            logger.info('Starting data transmission to server')
            if not self.connect_to_server():
                raise Exception("Could not connect to server")

            message = Message.data(0, data)
            message.set_timeout(2)

            logger.debug(f"Sending data to server: {data}")
            send_message(message, self.socket)

            response = recv_message(self.socket)
            while (not response or response.get_error_code() == ErrorCode.MISSING_DATA) and not message.is_timeout():
                if response and response.get_error_code() == ErrorCode.MISSING_DATA:
                    send_message(message, self.socket)

                logger.debug("Retrying to receive server response...")
                response = recv_message(self.socket)

            if response is None:
                raise Exception("Could not receive server response")
            elif response.get_error_code():
                raise Exception(
                    f"Error sending data: {response.get_error_code().name}")

            return True

        except Exception as e:
            logger.exception(e)
            logger.debug(f"Error sending data: {str(e)}")
            return False
        finally:
            self.disconnect_from_server()
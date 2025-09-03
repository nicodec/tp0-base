from .message import TOTAL_BYTES_LENGTH, Message
import logging

logger = logging.getLogger(__name__)

def recv_message(socket, timeout=1):
    socket.settimeout(timeout)
    try:
        raw_message = socket.recv(TOTAL_BYTES_LENGTH)
        logger.debug(f"Received message: {len(raw_message)}")
        if not raw_message:
            return None
        message = Message.from_bytes(raw_message)
        return message
    except TimeoutError:
        return None


def send_message(message, socket, timeout=0.1):
    message.set_timeout(timeout)
    bytes_to_send = message.to_bytes()
    logger.debug(f"Sending message: {len(bytes_to_send)}")
    return socket.send(bytes_to_send)


def send_ack(secNumber, socket):
    ack_message = Message.ack(secNumber)
    send_message(ack_message, socket)


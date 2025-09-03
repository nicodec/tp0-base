from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

SEQUENCE_NUMBER_BYTES = 4
DATA_MAX_SIZE = 7991

TOTAL_BYTES_LENGTH = 1 + SEQUENCE_NUMBER_BYTES + SEQUENCE_NUMBER_BYTES + DATA_MAX_SIZE


class MessageType(Enum):
    DATA = 1
    ACK = 2
    ACK_END = 3
    ERROR = 4
    END = 5


class ErrorCode(Enum):
    MISSING_DATA = 1
    FILE_TOO_BIG = 2


class Message:
    def __init__(self, msg_type, seq_number=0, data=None, timeout=0, data_size=0):
        """
        Initialize a message

        Args:
            msg_type: Message type (MessageType)
            seq_number: Sequence number (for DATA/ACK)
            data: Message data
            timeout: Time in seconds until message expires
        """
        self.type = msg_type
        self.seq_number = seq_number
        self.data = data if data is not None else b''
        self.data_size = len(self.data) if not data_size else data_size

        # Verify maximum data size
        if self.data and self.data_size > DATA_MAX_SIZE:
            logger.error(
                f"Maximum data size is {DATA_MAX_SIZE} bytes, "
                f"received: {self.data_size}"
            )
            raise ValueError(
                f"Maximum data size is {DATA_MAX_SIZE} bytes"
            )

        # Tiempo de expiración para el mensaje
        self.timeout_time = datetime.now() + timedelta(seconds=timeout)

    def __repr__(self):
        """Representación textual del mensaje"""
        basic = f"Message(type={self.type.name}, seq_number={self.seq_number}"

        if self.type == MessageType.ERROR:
            basic += f", error_code={self.get_error_code().name}"
        elif self.data:
            if len(self.data) > 20:
                data_preview = self.data[:20]
                basic += f", data={data_preview}..."
            else:
                basic += f", data={self.data}"

        return basic + ")"

    def to_bytes(self):
        """Convierte el mensaje a bytes para enviar por la red"""
        # Crear un bytearray con el tipo de mensaje (1 byte)
        result = bytearray(self.type.value.to_bytes(1, 'big'))

        # Añadir el número de secuencia (4 bytes)
        result.extend(self.seq_number.to_bytes(SEQUENCE_NUMBER_BYTES, 'big'))

        result.extend(self.data_size.to_bytes(SEQUENCE_NUMBER_BYTES, 'big'))

        # Añadir los datos
        if self.data:
            result.extend(self.data)

        return bytes(result)

    @classmethod
    def from_bytes(cls, data):
        """Creates a message from received bytes"""
        # First byte is the message type
        msg_type = MessageType(data[0])

        # Next 4 bytes are the sequence number
        seq_number = int.from_bytes(data[1:SEQUENCE_NUMBER_BYTES + 1], 'big')
        # Next 4 bytes are the data size
        data_size = int.from_bytes(data[SEQUENCE_NUMBER_BYTES + 1:2 * SEQUENCE_NUMBER_BYTES + 1], 'big')
        # The rest is data
        if len(data) > 2 * SEQUENCE_NUMBER_BYTES + 1:
            msg_data = data[2 * SEQUENCE_NUMBER_BYTES + 1:]
        else:
            msg_data = b''

        return cls(msg_type, seq_number, msg_data, data_size=data_size)

    # Métodos de acceso simplificados

    def get_type(self):
        """Returns the message type"""
        return self.type

    def get_seq_number(self):
        """Returns the sequence number"""
        return self.seq_number

    def get_data(self):
        """Returns the message data"""
        return self.data

    def get_data_size(self):
        """Returns the message data size"""
        return self.data_size

    def get_data_as_string(self):
        """Returns data as UTF-8 string"""
        if not self.data:
            return ""
        return self.data.decode('utf-8')

    def get_error_code(self):
        """Extracts error code from message"""
        if self.type == MessageType.ERROR and self.data:
            error_value = int.from_bytes(self.data, 'big')
            return ErrorCode(error_value)
        return None

    def is_timeout(self):
        """Checks if message has expired"""
        return datetime.now() > self.timeout_time

    def set_timeout(self, timeout):
        """Sets a new expiration time"""
        self.timeout_time = datetime.now() + timedelta(seconds=timeout)

    # Métodos de fábrica estáticos para crear mensajes específicos

    @staticmethod
    def data(seq_number, data):
        """Crea un mensaje de datos"""
        return Message(MessageType.DATA, seq_number, data.encode("utf-8"))

    @staticmethod
    def ack(seq_number):
        """Crea un mensaje de confirmación"""
        return Message(MessageType.ACK, seq_number)

    @staticmethod
    def error(error_code, seq_number = 0):
        """Crea un mensaje de error"""
        data = error_code.value.to_bytes(1, 'big')
        return Message(MessageType.ERROR, seq_number, data)

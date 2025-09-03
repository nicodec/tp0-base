import socket
import logging
import signal

from common.message import Message, ErrorCode
from common.socket_utils import recv_message, send_message
from common.utils import Bet, store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True
        self._client_socket = None

        signal.signal(signal.SIGTERM, self._handle_sigterm)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # the server
        while self._running:
            try:
                self._client_socket = self.__accept_new_connection()
                if self._client_socket:
                    self.__handle_client_connection(self._client_socket)
            except (KeyboardInterrupt, SystemExit):
                self._handle_sigterm()
            finally:
                self._client_socket = None

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            message = recv_message(socket=client_sock)
            if not message:
                return

            if message.get_data_size() != len(message.get_data()):
                logging.debug(f"action: receive_message | result: fail | error: {ErrorCode.MISSING_DATA}")
                message.set_timeout(2)
                send_message(Message.error(ErrorCode.MISSING_DATA, message.get_seq_number), client_sock)
                while not message.is_timeout() and (not message or message.get_data_size() != len(message.get_data())):
                    message = recv_message(socket=client_sock)

            message_data = message.get_data_as_string().split(',')

            bet = Bet(message_data[0], message_data[1], message_data[2], message_data[3], message_data[4], message_data[5])
            store_bets([bet])

            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')

            send_message(Message.ack(message.get_seq_number()), client_sock)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        try:
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except socket.error:
            return None

    def _handle_sigterm(self, signum, frame):
        """
        SIGTERM handler
        Starts the graceful shutdown process
        """
        self._running = False
        self._server_socket.close()
        if self._client_socket:
            self._client_socket.close()

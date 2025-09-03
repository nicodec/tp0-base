import logging
import os
from abc import ABC, abstractmethod

from infrastructure.client.client import Client

logger = logging.getLogger(__name__)

class BettingCommandUseCase(ABC):

    @abstractmethod
    def start_betting(self, client_id):
        raise NotImplementedError

class BettingCommandUseCaseImpl(BettingCommandUseCase):

    def __init__(self, client: Client):
        self.client = client

    def start_betting(self, client_id):
        nombre = os.getenv('NOMBRE')
        apellido = os.getenv('APELLIDO')
        documento = os.getenv('DOCUMENTO')
        nacimiento = os.getenv('NACIMIENTO')
        numero = os.getenv('NUMERO')

        if None in [nombre, apellido, documento, nacimiento, numero]:
            logger.error("Error: Required environment variables are missing")
            raise ValueError(
                "Error: Required environment variables (NOMBRE, APELLIDO, DOCUMENTO, NACIMIENTO or NUMERO) are missing")
        
        bet_data = f'{client_id},{nombre},{apellido},{documento},{nacimiento},{numero}'

        if self.client.send_data(bet_data):
            logger.info(f'action: apuesta_enviada | result: success | dni: {documento} | numero: {numero}')


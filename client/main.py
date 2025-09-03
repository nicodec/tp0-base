#!/usr/bin/env python3

import logging
import os

import yaml

from infrastructure.client.client import Client
from infrastructure.client.client_config import ClientConfig
from usecase.betting_command_usecase import BettingCommandUseCase, \
    BettingCommandUseCaseImpl

logger = logging.getLogger(__name__)

def initialize_config():
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file. 
    If at least one of the config parameters is not found a KeyError exception 
    is thrown. If a parameter could not be parsed, a ValueError is thrown. 
    If parsing succeeded, the function returns a ConfigParser object 
    with config parameters
    """

    # Load default config from file
    default_config = {}
    try:
        with open("config.yaml", 'r') as file:
            default_config = yaml.safe_load(file)
    except FileNotFoundError:
        default_config = {}


    config_params = {}
    try:
        config_params["server.address"] = os.getenv('SERVER_ADDRESS', default_config["server"]["address"])
        config_params["id"] = int(os.getenv('ID', default_config.get("id", 1)))
        config_params["loop.amount"] = os.getenv('LOOP_AMOUNT', default_config["loop"]["amount"])
        config_params["loop.period"] = os.getenv('LOOP_PERIOD', default_config["loop"]["period"])
        config_params["log.level"] = os.getenv('CLI_LOG_LEVEL', default_config["log"]["level"])
        config_params["batch.maxAmount"] = os.getenv('BATCH_MAX_AMOUNT', default_config["batch"]["maxAmount"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params


def main():
    config_params = initialize_config()
    logging_level = config_params["log.level"]

    initialize_log(logging_level)

    print_config(config_params)

    client_config = ClientConfig(
        server_address=config_params.get('server.address'),
        id=config_params.get('id')
    )

    betting_command: BettingCommandUseCase = BettingCommandUseCaseImpl(
        client=Client(client_config)
    )

    try:
        betting_command.start_betting(config_params.get('id'))
    except Exception as e:
        logger.error(f"Error during betting process: {str(e)}")


def print_config(config: dict) -> None:
    """
    Log config parameters at the beginning of the program to verify the configuration
    of the component
    """
    logger.info(
        f"action: config | result: success | "
        f"client_id: {config.get('id')} | "
        f"server_address: {config.get('server.address')} | "
        f"loop_amount: {config.get('loop.amount')} | "
        f"loop_period: {config.get('loop.period')} | "
        f"log_level: {config.get('log.level')}"
    )

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()

#!/usr/bin/python
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate docker-compose.yml with server and clients')
    parser.add_argument(
        '--filename',
        default="docker-compose.yml",
        help='Name of the output docker-compose file (default: docker-compose.yml)'
    )
    parser.add_argument(
        '--clients',
        type=int,
        default=1,
        help='Number of clients to generate (default: 1)'
    )
    return parser.parse_args()


def write_server_config(file):
    server_config = '''  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    volumes:
      - ./server/config.ini:/config.ini
    networks:
      - generator_network
'''
    file.write(server_config)


def write_clients(file, number_clients):
    for i in range(1, number_clients + 1):
        write_client(file, i)


def write_client(file, num):
    client_config = f'''  client{num}:
    container_name: client{num}
    image: client:latest
    environment:
      - CLI_ID=1
      - CLI_LOG_LEVEL=DEBUG
      - NOMBRE=Santiago Lionel
      - APELLIDO=Lorca
      - DOCUMENTO=30904465
      - NACIMIENTO=1999-03-17
      - NUMERO=7574
    volumes:
      - ./client/config.yaml:/config.yaml
    networks:
      - generator_network
    depends_on:
      - server
'''
    file.write(client_config)


def write_network_config(file):
    network_config = '''
networks:
  generator_network:
    name: generator_network
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
'''
    file.write(network_config)


def main():
    args = parse_arguments()

    print(f"Generating {args.filename} with {args.clients} clients.")

    with open(args.filename, 'w') as f:
        f.write("services:\n")

        # Define the server service
        write_server_config(f)

        # Define multiple client services
        write_clients(f, args.clients)

        write_network_config(f)

    print(f"Generated {args.filename} with {args.clients} clients.")

if __name__ == '__main__':
    main()

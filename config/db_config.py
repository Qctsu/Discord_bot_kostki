import os
import socket
import json
import logging

from src.utils.logging_config import setup_logging

# Ustawienie logowania dla logów typu 'bot'
setup_logging(log_type='bot')

# Wczytywanie konfiguracji z pliku config.json
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
config_path = os.path.join(base_dir, 'config', 'config.json')
try:
    with open(config_path) as config_file:
        config = json.load(config_file)
except Exception as err:
    logging.error(f"Error reading config file: {err}")
    raise


def get_database_path():
    """
    Zwraca odpowiednią ścieżkę do bazy danych w zależności od środowiska.
    """
    try:
        # uruchamianie bota w docker
        if os.getenv("RUNNING_IN_DOCKER"):
            db_path = config['development_docker_database_path']
            logging.info("Running in Docker. Using development Docker database path.")
        # uruchamianie bota lokalnie
        elif socket.gethostname() == config['server_hostname']:
            db_path = config['production_database_path']
            logging.info("Running on production server. Using production database path.")
        # uruchamianie bota na serwerze
        else:
            db_path = config['development_database_path']
            logging.info("Running on development environment. Using development database path.")

        logging.info(f"Database path: {db_path}")
        return db_path
    except Exception as e:
        logging.error(f"Error determining database path: {e}")
        raise

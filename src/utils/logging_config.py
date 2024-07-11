import os
import logging
from logging.handlers import TimedRotatingFileHandler
import json


def setup_logging(log_type='bot'):
    """
    Konfiguruje logowanie w zależności od typu logów.

    Args:
    log_type (str): Typ logów (bot, rolls, error, access)
    """
    # Ustal ścieżkę do katalogu głównego projektu
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Tworzenie katalogu logs, jeśli nie istnieje
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Ścieżka do pliku logów
    log_file_path = os.path.join(log_dir, f'{log_type}.log')
    error_log_file_path = os.path.join(log_dir, 'error.log')

    # Wczytywanie konfiguracji z pliku config.json
    config_path = os.path.join(base_dir, 'config', 'config.json')
    with open(config_path) as config_file:
        config = json.load(config_file)

    # Konfiguracja rotacji logów na podstawie pliku config.json
    log_rotation = config.get('log_rotation', {})
    when = log_rotation.get('when', 'midnight')
    interval = log_rotation.get('interval', 1)
    backup_count = log_rotation.get('backupCount', 30)

    # Konfiguracja logowania do pliku z rotacją logów
    info_handler = TimedRotatingFileHandler(log_file_path, when=when, interval=interval, backupCount=backup_count)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    info_handler.addFilter(lambda record: record.levelno < logging.ERROR)

    # Konfiguracja logowania błędów do oddzielnego pliku z rotacją
    error_handler = TimedRotatingFileHandler(error_log_file_path, when=when, interval=interval,
                                             backupCount=backup_count, encoding='utf-8', delay=False)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Podstawowa konfiguracja logowania
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Ustawienia na DEBUG, aby wszystkie poziomy logów były przechwytywane
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    # Dodanie StreamHandlera do loggera głównego
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(stream_handler)

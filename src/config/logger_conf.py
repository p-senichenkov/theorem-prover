import logging


def configure_logger() -> None:
    logging.basicConfig(filename='latest.log', level=logging.INFO, format='')

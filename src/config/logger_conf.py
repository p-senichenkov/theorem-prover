import logging


# Default mode: write Info to file
def configure_logger() -> None:
    logging.basicConfig(filename='latest.log', level=logging.INFO, format='')


# Verbose mode: write Info to console
# def configure_logger() -> None:
#     logging.basicConfig(level=logging.INFO, format='')

# Extra verbose mode: write Debug to console
# def configure_logger() -> None:
#     logging.basicConfig(level=logging.DEBUG, format='')

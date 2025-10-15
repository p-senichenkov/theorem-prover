from unittest import main

from tests.test_parser import ParserTests
from tests.test_transformations import TransformationsTests
from tests.test_resolution import ResolutionTests
from tests.test_unification import UnificationTests
from src.config.logger_conf import configure_logger

if __name__ == '__main__':
    configure_logger()
    main()

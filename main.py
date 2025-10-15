from sys import argv
from typing import Any
from logging import getLogger

from src.parser.parser import parser
from src.core.resolution import Resolution, TransformationInfo
from src.config.logger_conf import configure_logger
from src.core.resolution_info import ResolutionStep

logger = getLogger('__main__')


def clauses_to_str(clauses: list[Any]) -> str:
    return ', '.join(list(map(str, clauses)))


def print_transformations(trans_info: list[TransformationInfo]) -> None:
    print('** Formula transformations **')
    for i in range(len(trans_info)):
        tr_info = trans_info[i]
        print(f'{i}. {tr_info.text}:')
        print(f'\t{tr_info.lhs}   {tr_info.neg_rhs}')


def print_res_steps(res_steps: list[ResolutionStep]) -> None:
    print('** Resolution **')
    if len(res_steps) == 0:
        print('Resolution cannot be applied')
    else:
        for step in res_steps:
            logger.debug(f'{step!r}')
            print(step)
            clauses = Resolution.comb_clauses(step.new_clauses())
            if len(clauses) > 0:
                print(f'Clauses: {clauses_to_str(clauses)}')
            print()


if __name__ == '__main__':
    configure_logger()

    formula_str = ''
    if len(argv) > 1:
        formula_str = ' '.join(argv[1:])
    else:
        formula_str = input('Enter formula: ')
    formula = parser.parse(formula_str)
    resolution = Resolution(formula)
    result = resolution.resolution()

    print(f'* {formula} *')
    print_transformations(resolution.get_transformations_info())
    print(f'Clauses: {clauses_to_str(resolution.get_first_clauses())}\n')
    print_res_steps(resolution.get_resolution_steps())

    if (result):
        print('Formula proved.')
        exit(0)
    else:
        print('Formula cannot be proved')
        exit(5)

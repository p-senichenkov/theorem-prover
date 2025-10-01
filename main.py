from sys import argv
from tabulate import tabulate

from parser import parser
from resolution import Resolution
from logger_conf import configure_logger

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
    if (result):
        print('Formula proved.')
    else:
        print('Formula cannot be proved. Branches tried:')
        branches = [(i.lhs, i.neg_rhs, i.string_res()) for i in resolution.get_branch_info()]
        print(tabulate(branches, headers=['Left-hand side', 'Negated right-hand side',
                                          'Clauses left']))

from sys import argv

from parser import parser
from resolution import Resolution

if __name__ == '__main__':
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
        print(f'Formula cannot be proved. Clauses left: {list(map(str, resolution.get_clauses()))}')

from sys import argv

from parser import parser
from resolution import Resolution, TransformationInfo
from logger_conf import configure_logger


def print_step_by_step(trans_info: list[TransformationInfo]) -> None:
    print('** Formula transformations **')
    for i in range(len(trans_info)):
        tr_info = trans_info[i]
        print(f'{i}. {tr_info.text}:')
        print(f'\t{tr_info.lhs}   {tr_info.neg_rhs}')


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

    print_step_by_step(resolution.get_transformations_info())

    branch_infos = resolution.get_branch_info()
    if len(branch_infos) == 1:
        br = branch_infos[0]
        print('** Resolution **')
        print(f'Lhs: {br.lhs}')
        print(f'Negated Rhs: {br.neg_rhs}')
        if len(br.resolution_steps) == 0:
            print('Resolution cannot be applied.')
        else:
            print('Resolution steps:')
            br.print_resolution_steps(1)
    else:
        print('** Branches **')
        for i in range(len(branch_infos)):
            branch_info = branch_infos[i]
            print(f'Branch {i}:')
            print(f'\tLhs: {branch_info.lhs}')
            print(f'\tRhs: {branch_info.neg_rhs}')
            if len(br.resolution_steps) == 0:
                print('Resolution cannot be applied.')
            else:
                print('\tResolution steps:')
                branch_info.print_resolution_steps(2)
            print(f'\tResult: {branch_info.string_res()}')

    if (result):
        print('Formula proved.')
        exit(0)
    else:
        print('Formula cannot be proved')
        exit(5)

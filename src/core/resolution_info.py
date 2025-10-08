from collections import namedtuple

from src.model.abstract.token import Token
from src.model.formula_representation import Clause


class BranchInfo:

    def __init__(self, lhs: Token, neg_rhs: Token, res: str | list[Clause],
                 resolution_steps: list[(Clause, Clause)]):
        self.lhs = lhs
        self.neg_rhs = neg_rhs
        self.res = res
        self.resolution_steps = resolution_steps

    def string_res(self) -> str:
        if isinstance(self.res, str):
            return self.res
        return '[' + ', '.join(list(map(str, self.res))) + ']'

    def print_resolution_steps(self, num_tabs: int = 0) -> None:
        for res_step in self.resolution_steps:
            print('\t' * num_tabs + f'{res_step[0]} with {res_step[1]}')


TransformationInfo = namedtuple('TransformationInfo', ['text', 'lhs', 'neg_rhs'])

from collections import namedtuple

from src.model.abstract.token import Token
from src.model.formula_representation import Clause

# Substitute source instead of dest
UnifierInfo = namedtuple('UnifierInfo', ['source', 'dest'])


def pad_strings(a: str, b: str) -> (str, str):
    while len(a) < len(b):
        a += ' '
    while len(b) < len(a):
        b += ' '
    return a, b


class ResolutionStep:

    def __init__(self, clauses: list[Clause], lhs_idx: int, rhs_idx: int, new_clause,
                 unifiers: list[UnifierInfo]):
        self.clauses = clauses
        self.lhs_idx = lhs_idx
        self.rhs_idx = rhs_idx
        if self.rhs_idx < self.lhs_idx:
            self.lhs_idx, self.rhs_idx = self.rhs_idx, self.lhs_idx
        self.new_clause = new_clause
        self.unifiers = unifiers

    def new_clauses(self) -> list[Clause]:
        new_clauses = self.clauses[:]
        del new_clauses[self.lhs_idx]
        del new_clauses[self.rhs_idx - 1]
        if isinstance(self.new_clause, Clause):
            new_clauses.append(self.new_clause)
        elif self.new_clause is not None:
            new_clauses += self.new_clause
        return new_clauses

    def __repr__(self):
        return f'''Resolution step:
\tClauses before: {self.clauses}
\tLhs: {self.lhs_idx}
\tRhs: {self.rhs_idx}
\tNew clause: {self.new_clause}
\tUnifiers: {self.unifiers}'''

    def __str__(self):
        before_lhs = 0
        lhs_len = 0
        # After lhs end (2 is needed for comma after lhs)
        before_rhs = 2
        rhs_len = 0
        clauses_str = ''
        for i in range(len(self.clauses)):
            s = str(self.clauses[i])
            if (i == self.lhs_idx or i == self.rhs_idx) and len(s) == 1:
                s = f' {s}'
            clauses_str += s
            if i != len(self.clauses) - 1:
                clauses_str += ', '

            if i < self.lhs_idx:
                before_lhs += len(s) + 2
            elif i == self.lhs_idx:
                lhs_len = len(s)
            elif i < self.rhs_idx:
                before_rhs += len(s) + 2
            elif i == self.rhs_idx:
                rhs_len = len(s)

        before_left_slash = before_lhs + lhs_len - 2
        # After lhs end
        before_right_slash = before_rhs

        # Center between lhs and rhs
        center = before_lhs + lhs_len + before_rhs // 2
        new_clause_str = ''
        if self.new_clause is None:
            new_clause_str = 'nil'
        elif isinstance(self.new_clause, Clause):
            new_clause_str = str(self.new_clause)
        else:
            new_clause_str = ', '.join(list(map(str, self.new_clause)))
        before_new_clause = center - len(new_clause_str) // 2

        unifiers_str_1 = ''
        unifiers_str_2 = ''
        for unif in self.unifiers:
            unifiers_str_1 += f'  |{unif.dest}'
            unifiers_str_2 += f'  |{unif.source}'
            unifiers_str_1, unifiers_str_2 = pad_strings(unifiers_str_1, unifiers_str_2)

        return f'''{clauses_str}
{' ' * before_lhs}{'-' * lhs_len}{' ' * before_rhs}{'-' * rhs_len}
{' ' * before_left_slash}\\ {' ' * before_right_slash} /{unifiers_str_1}
{' ' * before_left_slash} \\{' ' * before_right_slash}/ {unifiers_str_2}
{' ' * before_new_clause}{new_clause_str}'''


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

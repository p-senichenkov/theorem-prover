from collections import namedtuple
from logging import getLogger

from src.model.formula_representation import *
from src.core.resolution_info import BranchInfo
from src.util import recursive_instances

logger = getLogger(__name__)

Replacement = namedtuple('Replacement', ['sk_fun', 'term'])


class SkolemovFunctionResolution:
    clauses = []
    branches_info = []

    @staticmethod
    def try_unify(a: Clause, b: Clause) -> (bool, list[Replacement]):
        logger.debug(f'Trying to unify {a} and {b}...')
        if a == b:
            return True, []
        if isinstance(a, SkolemovFunction):
            a_vars = a.get_args()
            # Variables cannot be bound at this moment
            b_vars = recursive_instances(b, Variable)
            for a_var in a_vars:
                if a_var not in b_vars:
                    return False, []
            logger.info(f'Unify: {b} instead of {a}')
            return True, [Replacement(a, b)]
        if isinstance(b, SkolemovFunction):
            return SkolemovFunctionResolution.try_unify(b, a)
        # Cases like a | sf(b) | d -> a | b | c | d
        if isinstance(a, NaryLogicalOp) and isinstance(b, NaryLogicalOp) and type(a) == type(b):
            logger.debug('\tN-ary case')
            a_ch = a.children()
            b_ch = b.children()
            unique_a_ch = list(set(a_ch) - set(b_ch))
            if len(unique_a_ch) == 1:
                unique_a_ch = unique_a_ch[0]
            else:
                unique_a_ch = type(a)(sorted(unique_a_ch, key=lambda ch: repr(ch)))
            unique_b_ch = list(set(b_ch) - set(a_ch))
            if len(unique_b_ch) == 1:
                unique_b_ch = unique_b_ch[0]
            else:
                unique_b_ch = type(b)(sorted(unique_b_ch, key=lambda ch: repr(ch)))
            if isinstance(unique_a_ch, SkolemovFunction):
                return True, [Replacement(unique_a_ch, unique_b_ch)]
            if isinstance(unique_b_ch, SkolemovFunction):
                return True, [Replacement(unique_b_ch, unique_a_ch)]
            return False, []
        if a.stem_eq(b):
            a_ch = a.children()
            b_ch = b.children()
            if len(a_ch) == len(b_ch):
                replacements = []
                for i in range(len(a_ch)):
                    res = SkolemovFunctionResolution.try_unify(a_ch[i], b_ch[i])
                    if not res[0]:
                        return False, []
                    replacements += res[1]
                return True, replacements
        return False, []

    def skolemov_function_resolution(self):
        for clause_a in self.clauses:
            for clause_b in self.clauses:
                replacements = try_unify(clause_a, clause_b)

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

    # Returns empty list if clauses cannot be unified
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

from logging import getLogger

from src.model.formula_representation import *
from src.util import recursive_instances, recursively_transform_children

logger = getLogger(__name__)


class PredicateResolution:

    def __init__(self, clauses: list[Clause]):
        self.clauses = clauses

    @staticmethod
    def substitute_sk_const(formula: Token, source: Variable | Constant,
                            dest: SkolemovConstant | Variable) -> Token:
        '''Substitute source instead of all occurences of dest in formula'''
        return recursively_transform_children(formula, lambda x: source if x == dest else x)

    @staticmethod
    def predicate_resolution_branches(lhs: Token, neg_rhs: Token) -> bool:
        vars = recursive_instances(lhs, Variable)
        vars += recursive_instances(neg_rhs, Variable)
        vars = list(set(vars))
        logger.debug(f'\tVariables: {vars}')

        consts = recursive_instances(lhs, Constant)
        consts += recursive_instances(neg_rhs, Constant)
        consts = list(set(consts))
        logger.debug(f'\tConstants: {consts}')

        sk_consts = recursive_instances(lhs, SkolemovConstant)
        sk_consts += recursive_instances(neg_rhs, SkolemovConstant)
        sk_consts = list(set(sk_consts))
        logger.debug(f'\tSkolemov constnts: {sk_consts}')

        branches = []

        def sub(source: Variable | Constant, dest: SkolemovConstant | Variable) -> None:
            logger.debug(f'\tSubstituting {source} instead of {dest}...')
            branches.append((PredicateResolution.substitute_sk_const(lhs, source, dest),
                             PredicateResolution.substitute_sk_const(neg_rhs, source, dest)))

        # Substitute constants and variables instead of Skolemov constants
        for var in vars + consts:
            for sk_const in sk_consts:
                sub(var, sk_const)
        # Substitute constants instead of variables
        for const in consts:
            for var in vars:
                sub(const, var)
        return branches

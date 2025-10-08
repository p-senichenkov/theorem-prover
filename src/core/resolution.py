import logging
from collections import namedtuple

from src.model.formula_representation import *
from src.core.transformations import *
from src.util import recursively_transform_children, recursive_search, recursive_instances
from src.core.propositional_resolution import PropositionalResolution
from src.core.predicate_resolution import PredicateResolution

logger = logging.getLogger(__name__)


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


class Resolution:
    transformations_info = []
    branches_info = []

    def transofrm(self, formula: Token) -> (Token, Token):
        if not isinstance(formula, ImplicationSign):
            raise TypeError(
                f'Resolution can only be applied to ImplicationSign, got {type(formula)}')
        lhs, rhs = formula.children()
        neg_rhs = Not([rhs])
        logger.info(f'Working with {lhs} and {neg_rhs}')

        save_tr_info = lambda s: self.transformations_info.append(
            TransformationInfo(s, lhs, neg_rhs))
        save_tr_info('Negate right-hand side')

        lhs = remove_logical_ops(lhs)
        neg_rhs = remove_logical_ops(neg_rhs)
        logger.info(f'Removed logical operations: {lhs} and {neg_rhs}')
        save_tr_info('Apply equivalences to get rid of non-trivial logical operations')

        lhs = narrow_negation(lhs)
        neg_rhs = narrow_negation(neg_rhs)
        logger.info(f'Narrowed negation: {lhs} and {neg_rhs}')
        save_tr_info('Use de-Morgan laws to narrow negation')

        lhs = standartize_var_names(lhs)
        neg_rhs = standartize_var_names(neg_rhs)
        logger.info(f'Standartized variable names: {lhs} and {neg_rhs}')
        save_tr_info('Rename bound variables so that all variable names are unique')

        lhs = skolemize(lhs)
        neg_rhs = skolemize(neg_rhs, [])
        logger.info(f'Skolemized: {lhs} and {neg_rhs}')
        save_tr_info('Get rid of existence quantifier (use Skolemov constants and functions)')

        lhs = remove_foralls(lhs)
        neg_rhs = remove_foralls(neg_rhs)
        logger.info(f'Removed universal quantifiers: {lhs} and {neg_rhs}')
        save_tr_info('Get rid of universal quantifiers')

        lhs = to_cnf(lhs)
        neg_rhs = to_cnf(neg_rhs)
        logger.info(f'Brought to CNF: {lhs} and {neg_rhs}')
        save_tr_info('Bring formula to CNF')

        lhs = remove_redundancy(lhs)
        neg_rhs = remove_redundancy(neg_rhs)
        logger.info(f'Removed redundancy: {lhs} and {neg_rhs}')
        save_tr_info('Get rid of redundancy')

        return (lhs, neg_rhs)

    def __init__(self, formula: Token):
        self.formula = formula

    def resolution(self) -> bool:
        was_predicate = recursive_search(self.formula, lambda t: isinstance(t, Quantifier))

        lhs, neg_rhs = self.transofrm(self.formula)

        constains_sc = lambda f: recursive_search(f, lambda t: isinstance(t, SkolemovConstant))
        branches = [(lhs, neg_rhs)]
        if was_predicate or constains_sc(lhs) or constains_sc(neg_rhs):
            logger.debug('Got predicate formula. Trying branches...')
            branches += PredicateResolution.predicate_resolution_branches(lhs, neg_rhs)
        else:
            logger.debug('Got propositional formula. Trying to resolve directly...')
        logger.debug(f'Resolution branches:')
        for i in range(len(branches)):
            logger.debug(f'{i}. {branches[i]}')
        self.branches_info = [BranchInfo(br[0], br[1], 'not tried', []) for br in branches]

        for i in range(len(branches)):
            logger.debug(f'Trying branch {i}...')
            prop_res = PropositionalResolution(branches[i][0], branches[i][1])
            self.branches_info[i].resolution_steps = prop_res.get_resolution_steps()
            if prop_res.propositional_resolution():
                self.branches_info[i].clauses_left = 'proved'
                return True
            else:
                self.branches_info[i].res = prop_res.get_clauses()
        return False

    def get_branch_info(self) -> list[BranchInfo]:
        return self.branches_info

    def get_transformations_info(self) -> list[TransformationInfo]:
        return self.transformations_info

from logging import getLogger

from src.model.formula_representation import *
from src.core.transformations import *
from src.util import recursively_transform_children, recursive_search, recursive_instances
from src.core.resolution_info import BranchInfo, TransformationInfo, ResolutionStep
from src.core.unification import Unification, short_first

logger = getLogger(__name__)


class Resolution:
    transformations_info = []
    branches_info = []
    resolution_steps = []
    clauses_left = []
    first_clauses = []

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

        lhs = standartize_var_names(lhs, set())
        neg_rhs = standartize_var_names(neg_rhs, set())
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

    @staticmethod
    def comb_clauses(clauses: list[Clause]) -> None:
        child_key = lambda ch: ch.name if isinstance(ch, Variable) else ''
        sort_children = lambda clause: Or(sorted(clause.children(), key=child_key)) if \
                isinstance(clause, Or) else clause

        clauses = list(map(sort_children, clauses))
        clauses = list(set(clauses))
        clauses = list(filter(lambda x: x is not None, clauses))
        clauses = list(
            filter(lambda x: not isinstance(x, Constant) or not x == CONSTANT_TRUE, clauses))
        clauses.sort(key=short_first)
        return clauses

    def resolution(self) -> bool:
        lhs, neg_rhs = self.transofrm(self.formula)
        clauses = Resolution.comb_clauses(break_to_clauses(lhs) + break_to_clauses(neg_rhs))
        self.first_clauses = clauses[:]
        while len(clauses) > 0:
            step = Unification.try_apply_resolution(clauses)
            if step is None:
                self.clauses_left = clauses
                return False
            self.resolution_steps.append(step)
            clauses = Resolution.comb_clauses(step.new_clauses())
        return True

    def get_branch_info(self) -> list[BranchInfo]:
        return self.branches_info

    def get_transformations_info(self) -> list[TransformationInfo]:
        return self.transformations_info

    def get_first_clauses(self) -> list[Clause]:
        return self.first_clauses

    def get_resolution_steps(self) -> list[ResolutionStep]:
        return self.resolution_steps

    def get_clauses_left(self) -> list[Clause]:
        return self.clauses_left

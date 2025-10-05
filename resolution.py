import logging
from collections import namedtuple

from formula_representation import *
from transformations import *
from util import recursively_transform_children, recursive_search, recursive_instances
from logger_conf import configure_logger

logger = logging.getLogger(__name__)

Clause = Or | Not | Atom


class PropositionalResolution:
    resolution_steps = []

    def __init__(self, lhs: Token, neg_rhs: Token):
        self.lhs = lhs
        self.neg_rhs = neg_rhs
        self.clauses = []

    def resolve(self, a: Clause, b: Clause) -> (bool, Clause | None, Clause | None):
        logger.debug(f'\tTrying to resolve {a} and {b}...')

        a_children = set()
        if isinstance(a, Or):
            a_children = set(a.children())
        else:
            a_children = {a}
        a_nots = set(filter(lambda ch: isinstance(ch, Not), a_children))
        a_other = a_children - a_nots

        b_children = set()
        if isinstance(b, Or):
            b_children = set(b.children())
        else:
            b_children = {b}
        b_nots = set(filter(lambda ch: isinstance(ch, Not), b_children))
        b_other = b_children - b_nots

        removed_something = False
        new_a_nots = set()
        for a_not in a_nots:
            inner = a_not.children()[0]
            if inner in b_other:
                self.resolution_steps.append((inner, a_not))
                logger.debug(f'\t\tFound match: {inner}')
                b_other.remove(inner)
                removed_something = True
            else:
                new_a_nots.add(a_not)

        new_a = new_a_nots | a_other
        if len(new_a) == 1:
            new_a = new_a.pop()
        elif len(new_a) == 0:
            new_a = None
        else:
            new_a = Or(list(new_a))

        new_b = b_nots | b_other
        if len(new_b) == 1:
            new_b = new_b.pop()
        elif len(new_b) == 0:
            new_b = None
        else:
            new_b = Or(list(new_b))

        logger.debug(f'\t\tResult: {new_a} and {new_b}')
        return (removed_something, new_a, new_b)

    def comb_clauses(self) -> None:
        child_key = lambda ch: ch.name if isinstance(ch, Variable) else ''
        sort_children = lambda clause: Or(sorted(clause.children(), key=child_key)) if \
                isinstance(clause, Or) else clause

        self.clauses = list(map(sort_children, self.clauses))
        self.clauses = list(set(self.clauses))
        self.clauses = list(filter(lambda x: x is not None, self.clauses))
        self.clauses = list(
            filter(lambda x: not isinstance(x, Constant) or not x.is_const_true(), self.clauses))
        self.clauses.sort(key=lambda token: len(token.children()))

    def propositional_resolution(self) -> bool:
        self.clauses = break_to_clauses(self.lhs)
        self.clauses += break_to_clauses(self.neg_rhs)
        self.comb_clauses()

        while True:
            logger.debug(f'Clauses: {list(map(str, self.clauses))}')
            removed_something = False
            for i in range(len(self.clauses)):
                for j in range(len(self.clauses)):
                    if i == j:
                        continue
                    # Assume that formula here is CNF
                    # This means that clause is Or | Atom
                    removed_something, new_a, new_b = self.resolve(self.clauses[i], self.clauses[j])
                    self.clauses[i] = new_a
                    self.clauses[j] = new_b
                    if removed_something:
                        break
                if removed_something:
                    break
            self.comb_clauses()
            if not len(self.clauses):
                return True
            if not removed_something:
                logger.info(f'Cannot prove formula. Clauses left: {list(map(str, self.clauses))}')
                return False

    def get_clauses(self) -> list[Clause]:
        return self.clauses

    def get_resolution_steps(self) -> list[(Clause, Clause)]:
        return self.resolution_steps


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
        neg_rhs = skolemize(neg_rhs)
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


if __name__ == '__main__':
    configure_logger()

    formula = ImplicationSign(
        Implication([Variable('P'), Implication([Variable('Q'), Variable('R')])]),
        Implication([And([Variable('P'), Variable('Q')]),
                     Variable('R')]))
    print(f'** {formula} **')
    res = Resolution(formula)
    result = res.resolution()
    print(result)
    if not result:
        print(f'Clauses left: {list(map(str, res.get_clauses()))}')

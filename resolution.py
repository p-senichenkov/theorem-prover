from formula_representation import *
from transformations import *
import logging

from logger_conf import configure_logger

logger = logging.getLogger(__name__)

def resolve(a: Or | Atom, b: Or | Atom) -> (bool, Or | Atom | None, Or | Atom | None):
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

def try_find_unificator(a: Token, b: Token) -> Token:
    # TODO: find unificator
    raise NotImplementedError()

class Resolution:
    def __init__(self, formula: Token):
        self.formula = formula
        self.clauses = []

    def comb_clauses(self):
        self.clauses = list(set(self.clauses))
        self.clauses = list(filter(lambda x: x is not None, self.clauses))
        self.clauses.sort(key=lambda token: len(token.children()))

    def resolution(self) -> bool:
        if not isinstance(self.formula, ImplicationSign):
            raise TypeError(f'Resolution can only be applied to ImplicationSign, got {type(self.formula)}')
        lhs, rhs = self.formula.children()
        neg_rhs = Not([rhs])
        logger.info(f'Working with {lhs} and {neg_rhs}')

        lhs = remove_logical_ops(lhs)
        neg_rhs = remove_logical_ops(neg_rhs)
        logger.info(f'Removed logical operations: {lhs} and {neg_rhs}')

        lhs = narrow_negation(lhs)
        neg_rhs = narrow_negation(neg_rhs)
        logger.info(f'Narrowed negation: {lhs} and {neg_rhs}')

        lhs = standartize_var_names(lhs)
        neg_rhs = standartize_var_names(neg_rhs)
        logger.info(f'Standartized variable names: {lhs} and {neg_rhs}')

        lhs = skolemize(lhs)
        neg_rhs = skolemize(neg_rhs)
        logger.info(f'Skolemized: {lhs} and {neg_rhs}')

        lhs = remove_foralls(lhs)
        neg_rhs = remove_foralls(neg_rhs)
        logger.info(f'Removed universal quantifiers: {lhs} and {neg_rhs}')

        lhs = to_cnf(lhs)
        neg_rhs = to_cnf(neg_rhs)
        logger.info(f'Brought to CNF: {lhs} and {neg_rhs}')

        self.clauses = break_to_clauses(lhs)
        self.clauses += break_to_clauses(neg_rhs)
        self.comb_clauses()
        logger.info(f'Clauses: {' and '.join(list(map(str, self.clauses)))}')

        while True:
            logger.debug(f'Clauses: {list(map(str, self.clauses))}')
            removed_something = False
            for i in range(len(self.clauses)):
                for j in range(len(self.clauses)):
                    if i == j:
                        continue
                    # Only propositional formulas for now

                    # Assume that formula here is CNF
                    # This means that clause is Or | Atom
                    removed_something, new_a, new_b = resolve(self.clauses[i], self.clauses[j])
                    self.clauses[i] = new_a
                    self.clauses[j] = new_b
                    if removed_something:
                        break
                if removed_something:
                    break
            if not removed_something:
                logger.info(f'Cannot prove formula. Clauses left: {list(map(str, self.clauses))}')
                return False
            self.comb_clauses()
            if not len(self.clauses):
                return True

    def get_clauses(self) -> list[Or | Atom]:
        return self.clauses

if __name__ == '__main__':
    configure_logger()

    formula = ImplicationSign(
        Implication([
            Variable('P'),
            Implication([Variable('Q'), Variable('R')])
            ]),
        Implication([
            And([Variable('P'), Variable('Q')]),
            Variable('R')
            ])
        )
    print(f'** {formula} **')
    res = Resolution(formula)
    result = res.resolution()
    print(result)
    if not result:
        print(f'Clauses left: {list(map(str, res.get_clauses()))}')

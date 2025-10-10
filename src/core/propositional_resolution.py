from logging import getLogger

from src.model.formula_representation import *
from src.core.transformations import break_to_clauses

logger = getLogger(__name__)


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
            filter(lambda x: not isinstance(x, Constant) or not x == CONSTANT_TRUE, self.clauses))
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

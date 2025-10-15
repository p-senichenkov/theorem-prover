from logging import getLogger

from src.model.formula_representation import *
from src.core.resolution_info import UnifierInfo, ResolutionStep
from src.util import recursively_substitute

logger = getLogger(__name__)


# Short clauses are processed first, while repr ensures that right pairs are formed
def short_first(ch: Token):
    if isinstance(ch, Not):
        ch = ch.children()[0]
    return (len(ch.children()), repr(ch))


class Unification:
    # Check if two clauses can be unified to be *same*
    # NOTE: this method doesn't substitute unifier, so it can give false positives
    @staticmethod
    def try_unify_to_same(a: Clause, b: Clause) -> (bool, list[UnifierInfo]):
        logger.debug(f'\t\t\tTrying to unify to same {a} and {b}')
        if a == b:
            return True, []
        # Substitute constant instead of variable
        if isinstance(a, Constant) and isinstance(b, Variable):
            return True, [UnifierInfo(a, b)]
        # Substitute constant or variable instead of Skolemov constant
        if isinstance(a, Constant | Variable) and isinstance(b, SkolemovConstant):
            return True, [UnifierInfo(a, b)]
        # Substitute anything instead of Skolemov function
        if isinstance(b, SkolemovFunction):
            return True, [UnifierInfo(a, b)]
        # Skolemov function, cases like a | f(b) | d -> a | b | c | d
        if isinstance(a, NaryLogicalOp) and isinstance(b, NaryLogicalOp) and type(a) == type(b):
            a_ch = set(a.children())
            b_ch = set(b.children())
            unique_a_ch = sorted(list(a_ch - b_ch), key=repr)
            new_a = []
            if len(unique_a_ch) == 0:
                # len(unique_b_ch) > 0, because we've checked a == b already
                # WARN: in theory, we can substitute a | f(x) | b -> a | False | b
                return False, []
            elif len(unique_a_ch) == 1:
                new_a = unique_a_ch[0]
            else:
                new_a = type(a)(unique_a_ch)
            unique_b_ch = sorted(list(b_ch - a_ch), key=repr)
            new_b = []
            if len(unique_b_ch) == 0:
                return False, []
            elif len(unique_b_ch) == 1:
                new_b = unique_b_ch[0]
            else:
                new_b = type(b)(unique_b_ch)
            return Unification.try_unify_to_same(new_a, new_b)
        if a.stem_eq(b):
            a_ch = a.children()
            b_ch = b.children()
            if len(a_ch) == len(b_ch):
                replacements = []
                for i in range(len(a_ch)):
                    res, unif = Unification.try_unify_to_same(a_ch[i], b_ch[i])
                    if not res:
                        return False, []
                    replacements += unif
                return True, replacements
        return False, []

    # Check if two clauses can be unified to be *shorten* by resolution, i. e. "resolved"
    # NOTE: still can give false positives
    @staticmethod
    def try_resolve(a: Clause, b: Clause) -> (bool, list[UnifierInfo]):
        logger.debug(f'\tTrying to resolve {a} and {b}...')
        # a is negation of b, or vice versa
        if isinstance(a, FunctionOrPredicate | Atom) and isinstance(b, Not):
            res, unif = Unification.try_unify_to_same(a, b.children()[0])
            if res:
                return res, unif
            return Unification.try_unify_to_same(b.children()[0], a)
        if isinstance(b, FunctionOrPredicate | Atom) and isinstance(a, Not):
            res, unif = Unification.try_unify_to_same(b, a.children()[0])
            if res:
                return res, unif
            return Unification.try_unify_to_same(a.children()[0], b)

        # recursively go down
        if isinstance(a, Or) or isinstance(b, Or):
            a_ch = a.children() if isinstance(a, Or) else [a]
            b_ch = b.children() if isinstance(b, Or) else [b]
            for a_i in a_ch:
                for b_i in b_ch:
                    res, unif = Unification.try_resolve(a_i, b_i)
                    logger.info(f'\t{a_i} and {b_i} can{'' if res else 'not'} be resolved, unifiers: {unif}')
                    if res:
                        return True, unif
        return False, []

    # Checks if two clauses are unified and returns resolved clause
    @staticmethod
    def are_unified(a: Clause, b: Clause) -> (bool, (Clause | Clause) | Clause | None):
        # a is negation of b, or vice versa
        if isinstance(a, Not) and b == a.children()[0] or \
                isinstance(b, Not) and a == b.children()[0]:
            return True, None

        # recursively go down
        if isinstance(a, Or) or isinstance(b, Or):
            a_ch = a.children() if isinstance(a, Or) else [a]
            b_ch = b.children() if isinstance(b, Or) else [b]
            for i in range(len(a_ch)):
                for j in range(len(b_ch)):
                    res, new_clause = Unification.are_unified(a_ch[i], b_ch[j])
                    logger.debug(f'\t{a_ch[i]} and {b_ch[i]} are{'' if res else ' not'} unified, new clause: {new_clause}')
                    if res:
                        new_a_ch = a_ch[:]
                        new_b_ch = b_ch[:]
                        # if new_clause is None:
                        del new_a_ch[i]
                        del new_b_ch[j]
                        if new_clause is None:
                            pass
                        elif new_clause is Clause:
                            new_a_ch.append(new_clause)
                        else:
                            new_a_ch.append(new_clause[0])
                            new_b_ch.append(new_clause[1])
                        new_a = None
                        new_b = None
                        if len(new_a_ch) == 0:
                            new_a = None
                        elif len(new_a_ch) == 1:
                            new_a = new_a_ch[0]
                        else:
                            new_a = Or(new_a_ch)
                        if len(new_b_ch) == 0:
                            new_b = None
                        elif len(new_b_ch) == 1:
                            new_b = new_b_ch[0]
                        else:
                            new_b = Or(new_b_ch)

                        if new_a is None:
                            return True, new_b
                        if new_b is None:
                            return True, new_a
                        return True, (new_a, new_b)
        return False, None

    @staticmethod
    def try_apply_resolution(clauses: list[Clause]) -> ResolutionStep | None:
        clauses.sort(key=short_first)

        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                res, unif = Unification.try_resolve(clauses[i], clauses[j])
                logger.info(f'{clauses[i]} and {clauses[j]} can{'' if res else 'not'} be unified, unifiers: {unif}')
                if res:
                    new_a = clauses[i]
                    new_b = clauses[j]
                    for source, dest in unif:
                        new_a = recursively_substitute(new_a, source, dest)
                        new_b = recursively_substitute(new_b, source, dest)
                    are_unif, new_clause = Unification.are_unified(new_a, new_b)
                    if are_unif:
                        return ResolutionStep(clauses, i, j, new_clause, unif)
        # No resolution can be applied
        return None

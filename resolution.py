from formula_representation import *
from transformations import *

def resolve(a: Or | Atom, b: Or | Atom) -> (bool, Or | Atom | None, Or | Atom | None):
    print(f'\tTrying to resolve {a} and {b}...')

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
            print(f'\t\tFound match: not {inner} and {inner}')
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

    print(f'\t\tResult: {new_a} and {new_b}')
    return (removed_something, new_a, new_b)

def try_find_unificator(a: Token, b: Token) -> Token:
    # TODO: find unificator
    raise NotImplementedError()

def resolution(formula: Token) -> bool:
    if not isinstance(formula, ImplicationSign):
        raise TypeError(f'Resolution can only be applied to ImplicationSign, got {type(formula)}')
    lhs, rhs = formula.children()
    neg_rhs = Not([rhs])
    print(f'Working with {lhs} and {neg_rhs}')

    lhs = remove_logical_ops(lhs)
    neg_rhs = remove_logical_ops(neg_rhs)
    print(f'Removed logical operations: {lhs} and {neg_rhs}')

    lhs = narrow_negation(lhs)
    neg_rhs = narrow_negation(neg_rhs)
    print(f'Narrowed negation: {lhs} and {neg_rhs}')

    # TODO: "alpha-conversion"
    lhs = skolemize(lhs)
    neg_rhs = skolemize(neg_rhs)
    print(f'Skolemized: {lhs} and {neg_rhs}')

    lhs = remove_foralls(lhs)
    neg_rhs = remove_foralls(neg_rhs)
    print(f'Removed universal quantifiers: {lhs} and {neg_rhs}')

    lhs = to_cnf(lhs)
    neg_rhs = to_cnf(neg_rhs)
    print(f'Brought to CNF: {lhs} and {neg_rhs}')

    clauses = break_to_clauses(lhs)
    clauses += break_to_clauses(neg_rhs)
    clauses.sort(key=lambda token: len(token.children()))
    print(f'Clauses: {' and '.join(list(map(str, clauses)))}')

    while True:
        print(f'Clauses: {list(map(str, clauses))}')
        removed_something = False
        for i in range(len(clauses)):
            for j in range(len(clauses)):
                if i == j:
                    continue
                # Only propositional formulas for now

                # Assume that formula here is CNF
                # This means that clause is Or | Atom
                removed_something, new_a, new_b = resolve(clauses[i], clauses[j])
                clauses[i] = new_a
                clauses[j] = new_b
                if removed_something:
                    break
            if removed_something:
                break
        if not removed_something:
            return False
        clauses = list(filter(lambda x: x is not None, clauses))
        if not len(clauses):
            return True

if __name__ == '__main__':
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
    print(resolution(formula))

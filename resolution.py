from formula_representation import *
from transformations import *

def resolve(a: Or | Atom, b: Or | Atom) -> (bool, Or | Atom | None, Or | Atom | None):
    a_children = set()
    if isinstance(a, Or):
        a_children = set(a.children())
    else:
        a_children = {a}
    a_nots = set(filter(a_children, lambda ch: isinstance(ch, Not)))
    a_other = a_children - a_nots

    b_children = set()
    if isinstance(a, Or):
        b_children = set(b.children())
    else:
        b_children = {b}
    b_nots = set(filter(b_children, lambda ch: isinstance(ch, Not)))
    b_other = b_children - b_nots

    removed_something = False
    new_a_nots = set()
    for a_not in a_nots:
        inner = a_not.children()[0]
        if inner in b_other:
            b_other.remove(inner)
            removed_something = True
        else:
            new_a_nots.add(a_not)

    new_b_nots = set()
    for b_not in b_nots:
        inner = b_not.children()[0]
        if inner in a_other:
            a_other.remove(inner)
            removed_something = True
        else:
            new_b_nots.add(inner)

    new_a = new_a_nots | a_other
    if len(new_a) == 1:
        new_a = new_a[0]
    else:
        new_a = None
    
    new_b = new_b_nots | b_other
    if len(new_b) == 1:
        new_b = new_b[0]
    else:
        new_b = None
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
    print(f'Removed logical operations: {lhs}, {neg_rhs}')

    lhs = narrow_negation(lhs)
    neg_rhs = narrow_negation(neg_rhs)
    print(f'Narrowed negation: {lhs}, {neg_rhs}')

    # TODO: "alpha-conversion"
    lhs = skolemize(lhs)
    neg_rhs = skolemize(neg_rhs)
    print(f'Skolemized: {lhs}, {neg_rhs}')

    lhs = remove_foralls(lhs)
    neg_rhs = remove_foralls(neg_rhs)
    print(f'Removed universal quantifiers: {lhs}, {neg_rhs}')

    # TODO: CNF

    clauses = break_to_clauses(lhs)
    clauses += break_to_clauses(neg_rhs)
    print(f'Clauses: {list(map(str, clauses))}')

    while True:
        resolved = False
        new_clauses = []
        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                clause_a = clauses[i]
                clause_b = clauses[j]
                # Only propositional formulas for now

                # Assume that formula here is CNF
                # This means that clause is Or | Atom
                removed_something, new_a, new_b = resolve(clause_a, clause_b)
                if (removed_something):
                    resolved = True
                    if new_a is not None:
                        new_clauses.append(new_a)
                    if new_b is not None:
                        new_clauses.append(new_b)
        if not resolved:
            return False
        clauses = new_clauses
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

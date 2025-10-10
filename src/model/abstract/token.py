from collections.abc import Sequence


# Base class for all that can appear in formula
class Token:
    has_axioms = False

    def __str__(self):
        raise NotImplementedError(f'Unknown token: {type(self)}')

    def __repr__(self):
        raise NotImplementedError(f'Unknown token: {type(self)}')

    # Get all children Tokens
    def children(self) -> Sequence:
        return []

    # Replace child token
    def replace_child(self, num: int, new_child):
        pass

    def __eq__(self, other):
        return type(self) == type(other) and self.children() == other.children()

    # Tokens themselves are equal, children may differ
    def stem_eq(self, other):
        return type(self) == type(other)

    def __hash__(self):
        return hash(str(self))

    # Remove all kinds of redundancy (depending on type)
    def remove_redundancy(self):
        return self

    def apply_axioms(self, entire_formula):
        raise TypeError(f'{type(self)} has no axioms!')

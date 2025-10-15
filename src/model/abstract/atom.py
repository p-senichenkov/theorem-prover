from src.model.abstract.token import Token


class Atom(Token):

    # Atoms hve no stem
    def stem_eq(self, other) -> bool:
        return self == other

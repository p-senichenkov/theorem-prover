from src.model.abstract.token import Token
from src.model.abstract.quantifier import Quantifier


class Forall(Quantifier):
    '''Universal quantifier'''
    unicode_repr = '∀'
    text_repr = 'forall'

    def remove(self) -> Token:
        return self.body

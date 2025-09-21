from unittest import TestCase, main

from formula_representation import *
from resolution import resolution
from logger_conf import configure_logger

class ResolutionTests(TestCase):
    def test_simple_resolution(self):
        formula = ImplicationSign(Variable('x'), Variable('x'))
        self.assertTrue(resolution(formula))

    def test_more_complex_resolution(self):
        formula = ImplicationSign(
                Or([Variable('x'), Variable('y')]),
                Or([Variable('x'), Variable('y')])
                )
        self.assertTrue(resolution(formula))

    def test_resolution_textbook_example(self):
        # P -> (Q -> R) => (P & Q) -> R
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
        self.assertTrue(resolution(formula))

if __name__ == '__main__':
    configure_logger()
    main()

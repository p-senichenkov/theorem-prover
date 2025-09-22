from unittest import TestCase, main

from formula_representation import *
from resolution import Resolution
from logger_conf import configure_logger

class ResolutionTests(TestCase):
    def test_simple_resolution(self):
        formula = ImplicationSign(Variable('x'), Variable('x'))
        res = Resolution(formula)
        self.assertTrue(res.resolution())
        self.assertEqual(len(res.get_clauses()), 0)

    def test_more_complex_resolution(self):
        formula = ImplicationSign(
                Or([Variable('x'), Variable('y')]),
                Or([Variable('x'), Variable('y')])
                )
        res = Resolution(formula)
        self.assertTrue(res.resolution())
        self.assertEqual(len(res.get_clauses()), 0)

    def test_resolution_textbook_example_1(self):
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
        res = Resolution(formula)
        self.assertTrue(res.resolution())
        self.assertEqual(len(res.get_clauses()), 0)

    def test_resolution_textbook_example_2(self):
        # John didn't meet Smith last night only if either Smith is a killer or John lies.
        # Smith isn't a killer only if John didn't met Smith last night and a murder was commited
        # after midnight.
        # If murder was commited after midnight, then either Smith is a killer or John lies.
        # Thus, Smith is a killer
        formula = ImplicationSign([
            Implication([
                Variable('M'),
                Xor([Variable('K'), Variable('L')])
                ]),
            Implication([
                Not([Variable('K')]),
                And([Variable('M'), Variable('N')])
                ]),
            Implication([
                Variable('N'),
                Xor([Variable('K'), Variable('L')])
                ])
            ], Variable('K')
                )
        res = Resolution(formula)
        self.assertFalse(res.resolution())

if __name__ == '__main__':
    configure_logger()
    main()

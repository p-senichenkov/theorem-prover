from unittest import TestCase, main

from formula_representation import *
from transformations import *
from logger_conf import configure_logger

CHARS = {
        'exists': '∃',
        'forall': '∀',
        'not': '¬',
        'and': '&',
        'or': '∨',
        'pierce_arrow': '↑',
        }

class TransformationsTests(TestCase):
    def test_remove_logical_ops_pierce_arrow(self):
        formula = PierceArrow([Variable('x'), Variable('y')])
        expected = 'not((v_x) or (v_y))'
        actual = repr(remove_logical_ops(formula))
        self.assertEqual(actual, expected)

    def test_remove_logical_ops_implication(self):
        formula = Implication([Variable('x'), Variable('y')])
        expected = '(not(v_x)) or (v_y)'
        actual = repr(remove_logical_ops(formula))
        self.assertEqual(actual, expected)

    # This test also tests equivalence
    def test_remove_logical_ops_xor(self):
        formula = Xor([Variable('x'), Variable('y')])
        expected = 'not(((not(v_x)) or (v_y)) and ((not(v_y)) or (v_x)))'
        actual = repr(remove_logical_ops(formula))
        self.assertEqual(actual, expected)

    def test_narrow_negation_forall(self):
        formula = Not([Forall(Variable('x'), Variable('y'))])
        expected = 'exists v_x (not(v_y))'
        actual = repr(narrow_negation(formula))
        self.assertEqual(actual, expected)

    def test_narrow_negation_exists(self):
        formula = Not([Exists(Variable('x'), Variable('y'))])
        expected = 'forall v_x (not(v_y))'
        actual = repr(narrow_negation(formula))
        self.assertEqual(actual, expected)

    def test_narrow_negation_or(self):
        formula = Not([Or([Variable('x'), Variable('y')])])
        expected = '(not(v_x)) and (not(v_y))'
        actual = repr(narrow_negation(formula))
        self.assertEqual(actual, expected)

    def test_narrow_negation_and(self):
        formula = Not([And([Variable('x'), Variable('y')])])
        expected = '(not(v_x)) or (not(v_y))'
        actual = repr(narrow_negation(formula))
        self.assertEqual(actual, expected)

    def test_narrow_negation_not(self):
        formula = Not([Not([Variable('x')])])
        expected = 'v_x'
        actual = repr(narrow_negation(formula))
        self.assertEqual(actual, expected)

    def test_standartize_var_names(self):
        formula = Or([
            Variable('x'),
            Forall(Variable('x'), And([
                Exists(Variable('x'), Variable('y')),
                Forall(Variable('y'), Variable('x')),
                Forall(Variable('x'), Constant('x')),
                Variable('x')
                ])),
            Variable('x')
            ])
        expected = '(v_x) or (forall v_tmp0 ((exists v_tmp1 (v_y)) and (forall v_tmp2 ' + \
                f'(v_tmp0)) and (forall v_tmp3 (c_{repr('x')})) and (v_tmp0))) or (v_x)'
        actual = repr(standartize_var_names(formula))
        self.assertEqual(actual, expected)

    def test_skolemize(self):
        # TODO: skolemov functions
        formula = Exists(Variable('x'), Or([
            Equals([Variable('x'), Variable('z')]), Exists(Variable('x'), Not([
                Equals([Variable('x'), Variable('z')])
                                                                              ]))
                                                           ]))
        expected = '(equals(sc_c0, v_z)) or (not(equals(sc_c1, v_z)))'
        actual = repr(skolemize(formula))
        self.assertEqual(actual, expected)

    def test_remove_foralls(self):
        formula = Or([Forall(Variable('x'), Forall(Variable('y'), Equals([
            Variable('x'), Variable('y')
            ]))), Variable('z')])
        expected = '(equals(v_x, v_y)) or (v_z)'
        actual = repr(remove_foralls(formula))
        self.assertEqual(actual, expected)

    def test_merge_nary_ops(self):
        formula = Or([
            Or([
                Variable('x'), Or([
                    Variable('y'), Constant(True), Variable('z')
                    ]), And([
                        Variable('z'), And([
                            Constant(True), Constant(False)
                            ])
                        ])
                ])
            ])
        expected = f'(v_x) or (v_y) or (c_{True}) or (v_z) or ((v_z) and (c_{True}) and (c_{False}))'
        actual = repr(merge_nary_ops(formula))
        self.assertEqual(actual, expected)

    def test_distribute(self):
        formula = Or([
            Variable('A'),
            And([
                Variable('B'),
                Variable('C'),
                Variable('D')
                ]),
            And([
                Variable('E'),
                Variable('F')
                ])
            ])
        # A or (B and C and D) or (E and F) ->
        # (A or B or (E and F)) and (A or C or (E and F)) and (A or D or (E and F)) ->
        # ((A or B or E) and (A or B or F)) and ((A or C or E) and (A or C or F)) and ((A or D or E)
        #                                                                         and (A or D or F))
        expected = '(((v_A) or (v_B) or (v_E)) and ((v_A) or (v_B) or (v_F))) and ' + \
                '(((v_A) or (v_C) or (v_E)) and ((v_A) or (v_C) or (v_F))) and ' + \
                '(((v_A) or (v_D) or (v_E)) and ((v_A) or (v_D) or (v_F)))'
        actual = repr(distribute(formula))
        self.assertEqual(actual, expected)

    def test_to_cnf(self):
        formula = Or([
            Variable('A'),
            And([
                Variable('B'),
                And([
                    Variable('C'),
                    Variable('D')
                    ])
                ]),
            And([
                Variable('E'),
                Variable('F')
                ])
            ])
        # A or (B and C and D) or (E and F) ->
        # (A or B or (E and F)) and (A or C or (E and F)) and (A or D or (E and F)) ->
        # ((A or B or E) and (A or B or F)) and ((A or C or E) and (A or C or F)) and ((A or D or E)
        #                                                                         and (A or D or F))
        expected = '((v_A) or (v_B) or (v_E)) and ((v_A) or (v_B) or (v_F)) and ' + \
                '((v_A) or (v_C) or (v_E)) and ((v_A) or (v_C) or (v_F)) and ' + \
                '((v_A) or (v_D) or (v_E)) and ((v_A) or (v_D) or (v_F))'
        actual = repr(to_cnf(formula))
        self.assertEqual(actual, expected)

    def test_remove_redundancy_equals(self):
        formula = Equals([Variable('x'), Variable('x')])
        expected = f'c_{repr(True)}'
        actual = repr(remove_redundancy(formula))
        self.assertEqual(actual, expected)

    def test_remove_redundancy_A_and_F(self):
        formula = And([Variable('x'), Constant(False), Variable('y')])
        expected = f'c_{repr(False)}'
        actual = repr(remove_redundancy(formula))
        self.assertEqual(actual, expected)

    def test_remove_redundancy_A_and_T(self):
        formula = And([Variable('x'), Constant(True), Variable('y')])
        expected_vars = ['(v_x) and (v_y)', '(v_y) and (v_x)']
        actual = repr(remove_redundancy(formula))
        self.assertIn(actual, expected_vars)

    def test_remove_redundancy_A_and_A(self):
        formula = And([Variable('x'), Variable('x'), Variable('y')])
        expected_vars = ['(v_x) and (v_y)', '(v_y) and (v_x)']
        actual = repr(remove_redundancy(formula))
        self.assertIn(actual, expected_vars)

    def test_remove_redundancy_A_and_not_A(self):
        formula = And([Variable('x'), Not([Variable('x')]), Variable('y')])
        expected = f'c_{repr(False)}'
        actual = repr(remove_redundancy(formula))
        self.assertEqual(actual, expected)

    def test_remove_redundancy_A_or_T(self):
        formula = Or([Variable('x'), Constant(True), Variable('y')])
        expected = f'c_{repr(True)}'
        actual = repr(remove_redundancy(formula))
        self.assertEqual(actual, expected)

    def test_remove_redundancy_A_or_F(self):
        formula = Or([Variable('x'), Constant(False), Variable('y')])
        expected_vars = ['(v_x) or (v_y)', '(v_y) or (v_x)']
        actual = repr(remove_redundancy(formula))
        self.assertIn(actual, expected_vars)

    def test_remove_redundancy_A_or_A(self):
        formula = Or([Variable('x'), Variable('x'), Variable('y')])
        expected_vars = ['(v_x) or (v_y)', '(v_y) or (v_x)']
        actual = repr(remove_redundancy(formula))
        self.assertIn(actual, expected_vars)

    def test_remove_redundancy_A_or_not_A(self):
        formula = Or([Variable('x'), Not([Variable('x')]), Variable('y')])
        expected = f'c_{repr(True)}'
        actual = repr(remove_redundancy(formula))
        self.assertEqual(actual, expected)

    def test_break_to_clauses(self):
        formula = And([
            Equals([Variable('x'), Variable('y')]),
            And([Variable('z'), Or([Variable('t'), Variable('p')])])
            ])
        expected = ['equals(v_x, v_y)', 'v_z', '(v_t) or (v_p)']
        actual = list(map(repr, break_to_clauses(formula)))
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    configure_logger()

    main()

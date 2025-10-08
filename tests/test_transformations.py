from unittest import TestCase

from src.model.formula_representation import *
from src.core.transformations import *
from src.config.logger_conf import configure_logger

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
        Variable.reset_counter()
        formula = Or([
            Variable('x'),                              # x is free -- not replacing
            Forall(Variable('x'), And([                 # x is quantifier's variable -- replacing with tmp0
                Exists(Variable('x'), Variable('y')),   # x is quantifier's variable -- replacing  with tmp1, y is free
                Forall(Variable('y'), Variable('x')),   # x is bound -- replacing with tmp0, y is quantifier's variable -- replacing with tmp2
                Forall(Variable('x'), Constant('x')),   # x is quantifier's variable -- replacing with tmp3, second x is constant -- not replacing
                Variable('x')                           # x is bound -- replacing with tmp0
                ])),
            Variable('x')                               # x is free -- not replacing
            ])
        expected = '(v_x) or (forall v_tmp0 ((exists v_tmp1 (v_y)) and (forall v_tmp2 ' + \
                f'(v_tmp0)) and (forall v_tmp3 (c_{repr('x')})) and (v_tmp0))) or (v_x)'
        actual = repr(standartize_var_names(formula, set()))
        self.assertEqual(actual, expected)

    def test_skolemize_1(self):
        SkolemovConstant.reset_counter()
        formula = Exists(Variable('x'), Or([
            Equals([Variable('x'), Variable('z')]),
            Exists(Variable('x'), Not([
                Equals([Variable('x'), Variable('z')])
                                      ]))
                                           ]))
        expected = '(equals(sc_\'c0\', v_z)) or (not(equals(sc_\'c1\', v_z)))'
        actual = repr(skolemize(formula, []))
        self.assertEqual(actual, expected)

    def test_skolemize_2(self):
        SkolemovFunction.reset_counter()
        formula = Forall(Variable('y'),
            Exists(Variable('x'),
                CustomFunctionOrPredicate('P', [Variable('x'), Variable('y')])
                )
            )
        expected = 'forall v_y (cfp_P(sf_f0(v_y), v_y))'
        actual = repr(skolemize(formula, []))
        self.assertEqual(actual, expected)

    def test_skolemize_3(self):
        SkolemovConstant.reset_counter()
        SkolemovFunction.reset_counter()
        formula = Exists(Variable('x0'),
            Forall(Variable('y1'),
                Exists(Variable('x1'),
                    Forall(Variable('y2'),
                        Exists(Variable('x2'),
                            CustomFunctionOrPredicate('P', [
                                Variable('x0'), Variable('x1'), Variable('x2'),
                                Variable('y1'), Variable('y2')
                                ])
                            )
                        )
                    )
                )
            )
        expected = 'forall v_y1 (forall v_y2 (cfp_P(sc_\'c0\', sf_f0(v_y1), sf_f1(v_y1, v_y2), ' + \
                'v_y1, v_y2)))'
        # Variables somehow become [y] without [] here
        actual = repr(skolemize(formula, []))
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

    def test_remove_redundancy_And_single_operand(self):
        formula = And([Variable('x')])
        expected = 'v_x'
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

    def test_remove_redundancy_Or_single_operand(self):
        formula = Or([Variable('x')])
        expected = 'v_x'
        actual = repr(remove_redundancy(formula))
        self.assertEqual(actual, expected)

    def test_remove_redundancy_cascade(self):
        formula = And([
            Or([Variable('x'), Variable('y'), Not([Variable('x')])]),
            Variable('z')
            ])
        expected = 'v_z'
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

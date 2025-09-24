import ply.yacc as yacc

from lexer import tokens
from formula_representation import *

'''
formula : formula_side IMPLICATION_SIGN formula_side

formula_side : quantifier_complex
             | op_appl

quantifier_complex : quantifier VARIABLE (op_appl)

quantifier : FORALL
           | EXISTS

op_appl : (op_appl) binary_op (op_appl)
        | nary_op_and_appl: TODO: skip for now
        | prefix_op(comma_separated_list)
        | atom
        | empty

binary_op : PIERCE_ARROW
          | IMPLICATION
          | EQUIV
          | XOR

nary_op_and_appl : nary_op_and_appl nary_op (op_appl)
                 | (op_appl)

prefix_op : unary_logical_op
          | predicate
          | function

comma_separated_list : op_appl COMMA comma_separated_list
                     | op_appl

unary_logical_op : NOT

predicate : EQUALS
          | DIVBY

function : TODO

nary_op : AND
        | OR

atom : VARIABLE
     | CONSTANT

empty : EMPTY
'''

def p_formula(p):
    'formula : formula_side IMPLICATION_SIGN formula_side'
    p[0] = ImplicationSign(p[1], p[3])

def p_formula_side_quantifier_complex(p):
    'formula_side : quantifier_complex'
    p[0] = p[1]

def p_formula_side_op_appl(p):
    'formula_side : op_appl'
    p[0] = p[1]

def p_quantifier_complex(p):
    'quantifier_complex : quantifier VARIABLE L_PAREN op_appl R_PAREN'
    p[0] = p[1](Variable(p[2]), p[4])

def p_quantifier_forall(p):
    'quantifier : FORALL'
    p[0] = Forall

def p_quantifier_exists(p):
    'quantifier : EXISTS'
    p[0] = Exists

def p_op_appl_binary(p):
    'op_appl : L_PAREN op_appl R_PAREN binary_op L_PAREN op_appl R_PAREN'
    p[0] = p[4]([p[2], p[6]])

def p_op_appl_nary(p):
    'op_appl : nary_op_and_appl'
    p[0] = p[1]

def p_op_appl_prefix(p):
    'op_appl : prefix_op L_PAREN comma_separated_list R_PAREN'
    p[0] = p[1](p[3])

def p_op_appl_atom(p):
    'op_appl : atom'
    p[0] = p[1]

def p_op_appl_empty(p):
    'op_appl : empty'
    p[0] = p[1]

def p_binary_op_pierce_arrow(p):
    'binary_op : PIERCE_ARROW'
    p[0] = PierceArrow

def p_binary_op_implication(p):
    'binary_op : IMPLICATION'
    p[0] = Implication

def p_binary_op_equiv(p):
    'binary_op : EQUIV'
    p[0] = Equivalence

def p_binary_op_xor(p):
    'binary_op : XOR'
    p[0] = Xor

# FIXME: this looks very bad
def p_nary_op_and_appl_nary(p):
    'nary_op_and_appl : nary_op_and_appl nary_op L_PAREN op_appl R_PAREN'
    if isinstance(p[1], list):
        p[0] = p[2](p[1] + [p[4]])
    else:
        p[0] = p[2]([p[1]] + [p[4]])

def p_nary_op_and_appl_single(p):
    'nary_op_and_appl : L_PAREN op_appl R_PAREN'
    p[0] = p[2]

def p_prefix_op(p):
    '''prefix_op : unary_logical_op
                 | predicate'''
    # TODO: function
    # '''prefix_op : unary_logical_op
    #              | predicate
    #              | function'''
    p[0] = p[1]

def p_comma_separated_list_list(p):
    'comma_separated_list : op_appl COMMA comma_separated_list'
    p[0] = [p[1]] + p[3]

def p_comma_separated_list_single(p):
    'comma_separated_list : op_appl'
    p[0] = [p[1]]

def p_unary_logical_op_not(p):
    'unary_logical_op : NOT'
    p[0] = Not

def p_predicate_equals(p):
    'predicate : EQUALS'
    p[0] = Equals

def p_predicate_divby(p):
    'predicate : DIVBY'
    p[0] = DivisibleBy

def p_nary_op_and(p):
    'nary_op : AND'
    p[0] = And

def p_nary_op_or(p):
    'nary_op : OR'
    p[0] = Or

def p_atom_variable(p):
    'atom : VARIABLE'
    p[0] = Variable(p[1])

def p_atom_constant(p):
    'atom : CONSTANT'
    p[0] = Constant(eval(p[1]))

def p_empty(p):
    'empty : '
    pass

def p_error(p):
    print(f'Syntax error: {p}')
    exit(1)

parser = yacc.yacc()

if __name__ == '__main__':
    while True:
        try:
            s = input('formula> ')
        except EOFError:
            break
        if not s:
            continue
        result = parser.parse(s)
        print(repr(result))

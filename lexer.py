import ply.lex as lex

from formula_representation import *

ascii_ops = {
        'exists': 'EXISTS',
        'forall': 'FORALL',
        'equals': 'EQUALS',
        'divby': 'DIVBY',
        'not': 'NOT',
        'and': 'AND',
        'or': 'OR',
        'nor': 'PIERCE_ARROW',
        'nand': 'SHEFFER_STROKE',
        'implies': 'IMPLICATION',
        'equiv': 'EQUIV',
        'xor': 'XOR',
        'Implies': 'IMPLICATION_SIGN',
        }

# Only final classes are here
tokens = [
        'VARIABLE',
        'CONSTANT',
        'L_PAREN',
        'R_PAREN',
        'COMMA',
        'CUSTOM_FUNCTION_OR_PREDICATE'
        ] + list(ascii_ops.values())

# Fixed-character tokens
t_IMPLICATION_SIGN = r'\=\>|[|]-'

# Unicode mode
t_EXISTS = r'∃'
t_FORALL = r'∀'
t_EQUALS = r'\='
t_DIVBY = r'⋮'
t_NOT = r'¬|\!'
t_AND = r'\&'
t_OR = r'∨|[|]'
t_PIERCE_ARROW = r'↓'
t_SHEFFER_STROKE = r'↑'
t_IMPLICATION = r'→|\-\>'
t_EQUIV = r'↔|\<\-\>'
t_XOR = r'⊕'

# Service characters
t_L_PAREN = r'\('
t_R_PAREN = r'\)'
t_COMMA = r'\,'

def t_CUSTOM_FUNCTION_OR_PREDICATE(t):
    r'[p|f][_][a-zA-Z]+'
    t.value = t.value[2:]
    return t

def t_VARIABLE(t):
    r'[a-zA-Z]+'
    t.type = ascii_ops.get(t.value, 'VARIABLE')
    return t

def t_CONSTANT(t):
    r"['][\S]+[']"
    t.value = t.value[1:-1]
    return t

t_ignore = ' \t'

def t_error(t):
    print(f'Illegal character \'{t.value[0]}\'')
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    lexer.input(input())

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

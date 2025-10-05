# Theorem prover

A theorem prover based on resolution method.

## Usage

Simply type
```bash
python3 main.py
```

You will be prompted to enter formula to be proved.

Also you can give formula as an argument:
```bash
python3 main.py '((x) -> (y)) & (x) => y'
```
Don't forget quotes!

If you want to use formula from file, use the power of your shell:
```bash
python3 main.py <formula.txt
```

### Formula string representation

Typical formula looks like this: `(x) -> (y) => (z) & (x)`.
`=>` here is an implication that should be proved (you can also use "tack": `|-`, see table below).
We will call it "Implication" (capital I).
Formula cannot contain more than one Implication.
Formula without Implication is a statement that should be proven to be true, i. e. `x` is equvalent to `=> x`.

`->` is a binary logical operation named "implication", it will be replaced with `¬(x) ∨ (y)` later.

Operands of each logical operation (including negation) should be parenthesized.

Each identifier containing only alphabetical characters, which is not reserved (see table below) becomes a variable:
`x` is a variable.

Single-quoted identifier becomes a constant:
`'3'` and `'"Bob"` are constants (note: constants are `eval`uated, so strings should be double-quoted).

Custom functions and predicates should start with `f_` and `p_`: `p_IsEven`, `f_Increment`.
Such functions and predicated have no axioms and are defined only by name.

Quantifiers have form `forall x (z)`, i. e. only body is parenthesized.

Top-most conjunctions can be omitted, i. e. you can use a whitespace-separated list of clauses.

Theorem prover displays formulas in human-readable way, using a lot of Unicode characters.
But what if you don't have such characters on your keyboard?
The following table shows alternative represetations and short descriptions for all currently available operations.
You can use Unicode representation (e. g. copy characters from this table), string representation or any of alternative representations.
In other words, you can use any of back-ticked forms.

| Unicode | Name | String representation | Alternative representations |
| --- | --- | --- | --- |
| `=>` | Implication | `Implies` | `\|-` |
| `∃` | existance quantifier | `exists` | |
| `∀` | universal quantifier | `forall` | |
| `¬` | negation | `not` | `!` |
| `&` | conjunction | `and` | |
| `∨` | disjunction | `or` | `\|` |
| `→` | implication | `implies` | `->` |
| `↔` | equivalence | `equiv` | `<->` |
| `⊕` | exclusive or | `xor` | |
| `↓` | Pierce arrow | `nor` | |
| `↑` | Sheffer stroke | `nand` | |

Note that `|` is an alternative for disjunction, not for Sheffer stroke.
The only reason is convenience: disjunction is used more.

For more info on parsing see regexes in `lexer.py` and BNF in `parser.py`.

#### Parens

You may have noticed that formulas contain a lot of parens.
So why they cannot be skipped in situations like this: `(x) & (¬(y))` (you may want to write `x & ¬y`)?

Becuase it will make parser much more complicated, and parser here is not the main task.
You can look into `parser.py` and try to write BNF that will allow to omit parens (don't forget about precedence).

## Method used and output

Theorem prover is based on resolution method.
To prove formula it:
1. negates right-hand side of formula;
2. brings formula to a set of clauses;
3. tries to deduce `nil` from it.

Consider the following formula: `(x) -> (y) & (!(y)) => (!(x))`.
Output for it will be

```
** Formula transformations **
0. Negate right-hand side:
        &(((x) → (y)) & (¬(y)))   ¬(&(¬(x)))
1. Apply equivalences to get rid of non-trivial logical operations:
        &(((¬(x)) ∨ (y)) & (¬(y)))   ¬(&(¬(x)))
2. Use de-Morgan laws to narrow negation:
        &(((¬(x)) ∨ (y)) & (¬(y)))   ∨(x)
3. Rename bound variables so that all variable names are unique:
        &(((¬(x)) ∨ (y)) & (¬(y)))   ∨(x)
4. Get rid of existence quantifier (use Skolemov constants and functions):
        &(((¬(x)) ∨ (y)) & (¬(y)))   ∨(x)
5. Get rid of universal quantifiers:
        &(((¬(x)) ∨ (y)) & (¬(y)))   ∨(x)
6. Bring formula to CNF:
        ((¬(x)) ∨ (y)) & (¬(y))   ∨(x)
7. Get rid of redundancy:
        ((¬(x)) ∨ (y)) & (¬(y))   x
** Resolution **
Lhs: ((¬(x)) ∨ (y)) & (¬(y))
Negated Rhs: x
Resolution steps:
        y with ¬(y)
        x with ¬(x)
Formula proved.
```

Let's discuss it step-by-step.

### Formula transformations

The following steps are performed before applying resolution:

0. Negate right-hand side -- formula splitted into left-hand and right-hand sides; rhs is being negated.
1. Apply equivalences -- equivalences for logical operations are applied, so that formula contains only conjunction, disjunction and negation.
2. Narrow negation -- de-Morgan laws and quantifier equivalnces are applied to narrow negation as much as possible.
3. Standartize variable names -- bound variables are renamed so that all variable names in formula are unique.
4. "Skolemization" -- existance quantifiers are replaced with Skolemov constants and functions.
5. Get rid of universal quantifiers -- universal quantifiers are simply being removed.
6. Bring formula to CNF -- distributivity of disjunction is applied, so that formula becomes Conjunctive Normal Form.
Also, consecutive conjunctions or disjunctions are being merged into "n-ary" ones (by associativity) for brevity and convenience.
7. Get rid of redundancy -- different kinds of redundancies are removed (i. e. `(x) & (y) & (x)` is replaced with `y`).

It's recommended that you do these transformations when you try to prove formula on a piece of paper or on a whiteboard.

### Resolution

Resolution rule is being applied until `nil` is left, or there is nothing to resolve:
```
X ∨ A ∨ Y     Z ∨ ¬A ∨ T
       \       /
        \     /
     X ∨ Y ∨ Z ∨ T
```

Prover prints which terms were resolved (it will print "`A with ¬A`" here).

### Resolution branches

When prover gets predicate formula, it tries to substitute constants and variables instead of Skolemov constants and functions instead of variables.
Then it tries to apply resolution to each of such branches.

Prove succeeds on first successful branch.

import re
import itertools
from typing import Dict, Set, List, Tuple

class Expr:
    def eval(self, valuation: Dict[str, bool]) -> bool:
        raise NotImplementedError
    def vars(self) -> Set[str]:
        raise NotImplementedError

class Var(Expr):
    def __init__(self, name: str):
        self.name = name
    def eval(self, valuation):
        return bool(valuation[self.name])
    def vars(self):
        return {self.name}
    def __repr__(self):
        return self.name

class Not(Expr):
    def __init__(self, child: Expr):
        self.child = child
    def eval(self, valuation):
        return not self.child.eval(valuation)
    def vars(self):
        return self.child.vars()
    def __repr__(self):
        return f"(~{self.child})"

class And(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left; self.right = right
    def eval(self, valuation):
        return self.left.eval(valuation) and self.right.eval(valuation)
    def vars(self):
        return self.left.vars() | self.right.vars()
    def __repr__(self):
        return f"({self.left} & {self.right})"

class Or(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left; self.right = right
    def eval(self, valuation):
        return self.left.eval(valuation) or self.right.eval(valuation)
    def vars(self):
        return self.left.vars() | self.right.vars()
    def __repr__(self):
        return f"({self.left} | {self.right})"

class Implies(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left; self.right = right
    def eval(self, valuation):
        return (not self.left.eval(valuation)) or self.right.eval(valuation)
    def vars(self):
        return self.left.vars() | self.right.vars()
    def __repr__(self):
        return f"({self.left} -> {self.right})"

class Iff(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left; self.right = right
    def eval(self, valuation):
        return self.left.eval(valuation) == self.right.eval(valuation)
    def vars(self):
        return self.left.vars() | self.right.vars()
    def __repr__(self):
        return f"({self.left} <-> {self.right})"

# Lexer / Parser
_TOKEN_RE = re.compile(r'\s*(<->|->|[()~&|]|[A-Za-z_][A-Za-z0-9_]*|\S)')

def tokenize(s: str) -> List[str]:
    tokens = _TOKEN_RE.findall(s)
    if not tokens:
        return []
    return tokens

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def pop(self):
        t = self.peek()
        if t is not None:
            self.pos += 1
        return t

    # Grammar (precedence):
    # iff ::= imp ('<->' imp)*
    # imp ::= or_expr ('->' imp)?
    # or_expr ::= and_expr ('|' and_expr)*
    # and_expr ::= not_expr ('&' not_expr)*
    # not_expr ::= '~' not_expr | atom
    # atom ::= VAR | '(' iff ')'
    def parse(self) -> Expr:
        expr = self.parse_iff()
        if self.peek() is not None:
            raise ParserError(f"Unexpected token {self.peek()}")
        return expr

    def parse_iff(self):
        left = self.parse_imp()
        while self.peek() == '<->':
            self.pop()
            right = self.parse_imp()
            left = Iff(left, right)
        return left

    def parse_imp(self):
        left = self.parse_or()
        if self.peek() == '->':
            self.pop()
            right = self.parse_imp()
            return Implies(left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.peek() == '|':
            self.pop()
            right = self.parse_and()
            left = Or(left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek() == '&':
            self.pop()
            right = self.parse_not()
            left = And(left, right)
        return left

    def parse_not(self):
        if self.peek() == '~':
            self.pop()
            child = self.parse_not()
            return Not(child)
        return self.parse_atom()

    def parse_atom(self):
        t = self.peek()
        if t is None:
            raise ParserError("Unexpected end of input")
        if t == '(':
            self.pop()
            e = self.parse_iff()
            if self.pop() != ')':
                raise ParserError("Expected ')'")
            return e
        if re.match(r'[A-Za-z_][A-Za-z0-9_]*', t):
            self.pop()
            return Var(t)
        raise ParserError(f"Unexpected token {t}")

def parse(s: str) -> Expr:
    tokens = tokenize(s)
    if not tokens:
        raise ParserError("Expression vide")
    return Parser(tokens).parse()

# Valuation helpers
def all_valuations(vars_list: List[str]):
    for bits in itertools.product([False, True], repeat=len(vars_list)):
        yield dict(zip(vars_list, bits))

# Core verifier functions
def is_satisfiable(axioms: List[Expr], max_models: int = 10) -> Tuple[bool, List[Dict[str, bool]]]:
    vars_set = set()
    for a in axioms:
        vars_set |= a.vars()
    vars_list = sorted(vars_set)
    models = []
    for v in all_valuations(vars_list):
        if all(a.eval(v) for a in axioms):
            models.append(v)
            if len(models) >= max_models:
                break
    return (len(models) > 0, models)

def entails(axioms: List[Expr], proposition: Expr) -> bool:
    # axioms |= proposition iff every model of axioms satisfies proposition
    sat, models = is_satisfiable(axioms, max_models=1000000)
    # if axioms unsatisfiable, by classical logic they entail everything (ex falso)
    if not sat:
        return True
    # check all models (if many variables, we still enumerated up to many)
    vars_set = set()
    for a in axioms + [proposition]:
        vars_set |= a.vars()
    vars_list = sorted(vars_set)
    for v in all_valuations(vars_list):
        if all(a.eval(v) for a in axioms) and not proposition.eval(v):
            return False
    return True

def is_contradiction(expr: Expr) -> bool:
    vars_list = sorted(expr.vars())
    for v in all_valuations(vars_list):
        if expr.eval(v):
            return False
    return True

def is_tautology(expr: Expr) -> bool:
    vars_list = sorted(expr.vars())
    for v in all_valuations(vars_list):
        if not expr.eval(v):
            return False
    return True

def find_counterexample(axioms: List[Expr], proposition: Expr):
    vars_set = set()
    for a in axioms + [proposition]:
        vars_set |= a.vars()
    vars_list = sorted(vars_set)
    for v in all_valuations(vars_list):
        if all(a.eval(v) for a in axioms) and not proposition.eval(v):
            return v
    return None

# Convenience: parse many strings
def parse_all(strs: List[str]) -> List[Expr]:
    return [parse(s) for s in strs]

# Petit exemple d'utilisation (si exécuté en script)
if __name__ == "__main__":
    # Exemple: axiomes: A -> B, A ; proposition: B
    axioms_s = ["A -> B", "A"]
    prop_s = "B"
    axioms = parse_all(axioms_s)
    prop = parse(prop_s)
    sat, models = is_satisfiable(axioms, max_models=5)
    print("Axiomes:", axioms_s)
    print("Proposition:", prop_s)
    print("Axiomes satisfiables ?", sat)
    if sat:
        print("Exemples de modèles:", models)
    print("Les axiomes impliquent la proposition ?", entails(axioms, prop))
    ce = find_counterexample(axioms, prop)
    if ce:
        print("Contre-exemple:", ce)
    else:
        print("Pas de contre-exemple trouvé (entailment vérifié).")
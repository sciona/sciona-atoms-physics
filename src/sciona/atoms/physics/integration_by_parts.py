"""Exact symbolic integration-by-parts rewrite, preserving its residual integral."""
import ast
import re
import sympy as sp
from sciona.ghost.abstract import AbstractScalar
from sciona.ghost.registry import register_atom
from sciona.physics_ingest.source_symbolic import parse_source_srepr


def _checked_parse(source):
    # Some SymPy constructors sympify string arguments internally. Admit text
    # only as symbol/function names or numeric Float literals, never as an
    # expression argument to Integral, Derivative, arithmetic or functions.
    if not isinstance(source,str) or not source or len(source)>100000:
        raise ValueError('Bounded serialized expression required')
    try: tree=ast.parse(source,mode='eval')
    except (SyntaxError,RecursionError) as error: raise ValueError('Invalid expression syntax') from error
    allowed=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.args:
            first=node.args[0]
            if isinstance(first,ast.Constant) and isinstance(first.value,str):
                if node.func.id in ['Symbol','Function'] and first.value.isidentifier() and len(first.value)<=128:
                    allowed.add(id(first))
                elif node.func.id=='Float' and re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',first.value):
                    allowed.add(id(first))
    if any(isinstance(n,ast.Constant) and isinstance(n.value,str) and id(n) not in allowed for n in ast.walk(tree)):
        raise ValueError('Expression strings inside constructors are not allowed')
    return parse_source_srepr(source)


def witness_integration_by_parts(u_srepr: AbstractScalar, v_srepr: AbstractScalar,
                                 variable_srepr: AbstractScalar, constant_srepr: AbstractScalar) -> tuple[AbstractScalar, AbstractScalar]:
    return AbstractScalar(dtype='str'), AbstractScalar(dtype='str')


@register_atom(witness_integration_by_parts)
def integration_by_parts(u_srepr: str, v_srepr: str, variable_srepr: str,
                         constant_srepr: str) -> tuple[str, str]:
    """Return integrand and a formal antiderivative as safely parsed srepr ASTs.

    Inputs encode scalar commutative expressions u(x), v(x), a real Symbol x,
    and a scalar integration constant independent of x. Undefined functions
    and unevaluated residual integrals are supported by the reviewed grammar.
    Inputs are interpreted as ASTs without Python eval. Same-named symbols with
    conflicting assumptions are rejected. Nonfinite expressions are rejected.

    Conditional domain: u and v must be C1 on one common connected open real
    interval. The caller establishes that domain; this transformation does not
    discover poles, branches or convergence conditions. Complex-valued C1
    functions of the real variable are allowed. All other symbols are fixed
    parameters; the integration constant must be independent of x.

    Output integrand is u*dv/dx. Output primitive is u*v - Integral(v*du/dx,x)+C.
    The remaining integral is intentionally unevaluated: this is the original
    integration-by-parts transformation, not quadrature or a claim that a
    closed-form primitive exists. Differentiation of the returned expression
    is checked against the integrand before returning both serialized ASTs.
    """
    u, v, x, constant = [_checked_parse(s) for s in [u_srepr,v_srepr,variable_srepr,constant_srepr]]
    if not isinstance(x,sp.Symbol) or x.is_real is not True:
        raise ValueError('A real independent Symbol is required')
    expressions = [u,v,constant]
    for expression in expressions:
        if not isinstance(expression,sp.Expr) or expression.is_commutative is not True:
            raise ValueError('Scalar commutative expressions required')
        if expression.has(sp.nan,sp.oo,-sp.oo,sp.zoo):
            raise ValueError('Finite symbolic expressions required')
    identities = {}
    for symbol in {x}.union(*(e.free_symbols for e in expressions)):
        if symbol.name in identities and identities[symbol.name] != symbol:
            raise ValueError('Same-named symbols must have identical assumptions')
        identities[symbol.name] = symbol
    if x in constant.free_symbols:
        raise ValueError('Integration constant must be independent of the variable')
    # Keep derivatives formal in the portable AST. Eager chain rules can
    # introduce internal Subs/Dummy nodes outside the reviewed input grammar.
    du,dv=sp.Derivative(u,x,evaluate=False),sp.Derivative(v,x,evaluate=False)
    integrand = u*dv
    primitive = u*v-sp.Integral(v*du,x)+constant
    if integrand.has(sp.nan,sp.oo,-sp.oo,sp.zoo) or primitive.has(sp.nan,sp.oo,-sp.oo,sp.zoo):
        raise ValueError('Rewrite generated a nonfinite expression')
    residual = sp.expand((sp.diff(primitive,x)-integrand).xreplace({du:sp.diff(u,x),dv:sp.diff(v,x)}))
    if residual != 0:
        raise ValueError('Derivative verification did not establish the rewrite')
    serialized=sp.srepr(integrand),sp.srepr(primitive)
    for encoded in serialized:
        _checked_parse(encoded)
    return serialized

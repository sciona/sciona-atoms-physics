"""Symbolic Cartesian curl-curl identity with its divergence term retained."""
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


def witness_curl_curl(field_srepr: AbstractScalar, coordinates_srepr: AbstractScalar
                     ) -> tuple[AbstractScalar,AbstractScalar,AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_curl_curl)
def curl_curl(field_srepr: str, coordinates_srepr: str) -> tuple[str,str,str]:
    """Return curl(curl F), grad(div F), and component Laplacian as tuple ASTs.

    Inputs encode Tuple(Fx,Fy,Fz) of finite scalar commutative expressions and
    Tuple(x,y,z) of three distinct real Symbols, with consistent assumptions.
    Caller establishes C2 fields on a common open region in a fixed right-handed
    orthonormal Cartesian frame. Complex field representations are allowed.
    Other symbols are fixed parameters. All components share units; outputs
    have those units divided by spatial length squared. Units and smoothness
    are caller-established, not inferred from untyped symbolic expressions.

    Formal derivatives retain arbitrary composed functions in portable srepr.
    First output equals second minus third under the stated conditions. No
    divergence-free or Maxwell assumption is imposed. No curvilinear metric,
    distributional, boundary-value solver or throughput claim. Requires the
    symbolic extra. Expression strings inside constructors are rejected before
    parsing; poles and branch domains are not discovered by this transformation.
    """
    field,coordinates=map(_checked_parse,[field_srepr,coordinates_srepr])
    if not isinstance(field,sp.Tuple) or len(field)!=3:
        raise ValueError('Three field components required')
    if not isinstance(coordinates,sp.Tuple) or len(coordinates)!=3 or len(set(coordinates))!=3:
        raise ValueError('Three distinct Cartesian coordinates required')
    if any(not isinstance(q,sp.Symbol) or q.is_real is not True for q in coordinates):
        raise ValueError('Real Symbol coordinates required')
    for e in field:
        if not isinstance(e,sp.Expr) or e.is_commutative is not True or e.has(sp.nan,sp.oo,-sp.oo,sp.zoo):
            raise ValueError('Finite scalar commutative fields required')
    identities={}
    for symbol in set(coordinates).union(*(e.free_symbols for e in field)):
        if symbol.name in identities and identities[symbol.name]!=symbol:
            raise ValueError('Conflicting symbol assumptions')
        identities[symbol.name]=symbol
    def derivative(e,q):
        return sp.Derivative(e,q,evaluate=False)
    def curl(f):
        x,y,z=coordinates;a,b,c=f
        return (derivative(c,y)-derivative(b,z),derivative(a,z)-derivative(c,x),derivative(b,x)-derivative(a,y))
    double=sp.Tuple(*curl(curl(field)))
    div=sum(derivative(e,q) for e,q in zip(field,coordinates))
    grad=sp.Tuple(*(derivative(div,q) for q in coordinates))
    lap=sp.Tuple(*(sum(sp.Derivative(e,q,2,evaluate=False) for q in coordinates) for e in field))
    encoded=tuple(sp.srepr(e) for e in [double,grad,lap])
    for e in encoded:_checked_parse(e)
    return encoded

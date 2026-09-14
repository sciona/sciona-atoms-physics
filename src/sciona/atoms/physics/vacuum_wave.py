"""Symbolic vacuum electric-field wave equation sides and Gauss constraint."""
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


def witness_vacuum_wave(field_srepr: AbstractScalar, coordinates_srepr: AbstractScalar,
                        permeability_srepr: AbstractScalar, permittivity_srepr: AbstractScalar
                        ) -> tuple[AbstractScalar,AbstractScalar,AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_vacuum_wave)
def vacuum_wave(field_srepr: str, coordinates_srepr: str, permeability_srepr: str,
                permittivity_srepr: str) -> tuple[str,str,str]:
    """Construct vacuum wave-equation sides and the separate Gauss constraint.

    field_srepr encodes Tuple(Ex,Ey,Ez); coordinates_srepr encodes Tuple(x,y,z,t)
    of four distinct real Symbols. Each field component is scalar commutative
    and C2 on a caller-established common open Cartesian space-time region.
    Complex-valued representations of fields are allowed. Other symbols are
    fixed parameters. Coefficients encode provably positive real constants
    mu in H/m and epsilon in F/m, independent of all four coordinates.

    Outputs encode Tuple components of laplacian(E), mu*epsilon*partial_t^2(E),
    and scalar divergence(E). Derivatives stay formal for arbitrary smooth
    symbolic fields, including compositions. The caller interprets equality of
    the first two under the source Maxwell premises: zero charge/current and
    spatially/time-constant vacuum coefficients. The third must vanish for
    charge-free Gauss. Outputs are expressions, not a certification that the
    supplied field satisfies Maxwell equations. Wave-equation satisfaction
    alone is insufficient. This is the source differential transformation,
    not a PDE solver or initial/boundary-value simulation.

    SI electric-field components have units V/m, coordinates m and time s.
    Caller establishes dimensional consistency and smoothness; this function
    does not infer units, discover poles/branches or prove constitutive laws.
    Requires the symbolic extra. Constructor expression strings are rejected
    before parsing. No real-data or throughput claim.
    """
    field,coordinates,mu,eps=map(_checked_parse,[field_srepr,coordinates_srepr,permeability_srepr,permittivity_srepr])
    if not isinstance(field,sp.Tuple) or len(field)!=3:
        raise ValueError('Three field components required')
    if not isinstance(coordinates,sp.Tuple) or len(coordinates)!=4 or len(set(coordinates))!=4:
        raise ValueError('Four distinct space-time coordinates required')
    if any(not isinstance(q,sp.Symbol) or q.is_real is not True for q in coordinates):
        raise ValueError('Real Symbol coordinates required')
    expressions=[*field,mu,eps]
    for e in expressions:
        if not isinstance(e,sp.Expr) or e.is_commutative is not True or e.has(sp.nan,sp.oo,-sp.oo,sp.zoo):
            raise ValueError('Finite scalar commutative expressions required')
    identities={}
    for symbol in set(coordinates).union(*(e.free_symbols for e in expressions)):
        if symbol.name in identities and identities[symbol.name]!=symbol:
            raise ValueError('Conflicting symbol assumptions')
        identities[symbol.name]=symbol
    for coefficient in [mu,eps]:
        if coefficient.is_positive is not True or coefficient.free_symbols.intersection(coordinates):
            raise ValueError('Positive constant vacuum coefficients required')
    x,y,z,t=coordinates
    left=sp.Tuple(*(sum(sp.Derivative(e,q,2,evaluate=False) for q in [x,y,z]) for e in field))
    right=sp.Tuple(*(mu*eps*sp.Derivative(e,t,2,evaluate=False) for e in field))
    div=sum(sp.Derivative(e,q,evaluate=False) for e,q in zip(field,[x,y,z]))
    encoded=tuple(sp.srepr(e) for e in [left,right,div])
    for e in encoded:_checked_parse(e)
    return encoded

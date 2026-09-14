"""Cartesian time-harmonic vector-field Helmholtz reduction."""
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



def witness_helmholtz(amplitude_srepr: AbstractScalar, coordinates_srepr: AbstractScalar,
                      angular_frequency_srepr: AbstractScalar, wave_speed_srepr: AbstractScalar
                      ) -> tuple[AbstractScalar,AbstractScalar,AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_helmholtz)
def helmholtz(amplitude_srepr: str, coordinates_srepr: str, angular_frequency_srepr: str,
              wave_speed_srepr: str) -> tuple[str,str,str]:
    """Return Tuple ASTs for U exp(i omega t), Laplacian(U), and Helmholtz residual.

    U is a Tuple of three scalar commutative spatial components, independent of
    time. Coordinates are Tuple(x,y,z,t) of distinct real Symbols. Real constant
    omega may be zero or negative; wave speed c must be positive, both independent
    of all coordinates. The residual is Laplacian(U)+(omega/c)^2 U. The wave
    residual equals this residual times exp(+i omega t); no zero residual is
    assumed. Derivatives remain formal to support arbitrary composed C2 fields.

    Caller establishes a common open Cartesian C2 domain and consistent units:
    U electric-field units, x/y/z length, t time, omega inverse time, c speed.
    Other symbols are fixed parameters. Complex amplitudes are allowed; the real
    part gives a real harmonic representation. Does not infer units, poles or
    branch domains, solve a boundary problem, or certify Maxwell divergence.
    Source mu*epsilon=1/c² assumes constant coefficients. Requires symbolic extra.
    """
    field,coords,w,c=map(_checked_parse,[amplitude_srepr,coordinates_srepr,angular_frequency_srepr,wave_speed_srepr])
    if not isinstance(field,sp.Tuple) or len(field)!=3:
        raise ValueError('Three spatial amplitudes required')
    if not isinstance(coords,sp.Tuple) or len(coords)!=4 or len(set(coords))!=4:
        raise ValueError('Four distinct coordinates required')
    if any(not isinstance(q,sp.Symbol) or q.is_real is not True for q in coords):
        raise ValueError('Real Symbol coordinates required')
    expressions=[*field,w,c]
    if any(not isinstance(e,sp.Expr) or e.is_commutative is not True or e.has(sp.nan,sp.oo,-sp.oo,sp.zoo) for e in expressions):
        raise ValueError('Finite commutative scalar expressions required')
    identities={}
    for symbol in set(coords).union(*(e.free_symbols for e in expressions)):
        if symbol.name in identities and identities[symbol.name]!=symbol:
            raise ValueError('Conflicting symbol assumptions')
        identities[symbol.name]=symbol
    if w.is_real is not True or c.is_positive is not True:
        raise ValueError('Real frequency and positive speed required')
    if any(e.free_symbols.intersection(coords) for e in [w,c]):
        raise ValueError('Frequency and speed must be coordinate independent')
    if any(coords[3] in e.free_symbols for e in field):
        raise ValueError('Amplitude must be time independent')
    phase=sp.exp(sp.I*w*coords[3])
    harmonic=sp.Tuple(*(e*phase for e in field))
    lap=sp.Tuple(*(sum(sp.Derivative(e,q,2,evaluate=False) for q in coords[:3]) for e in field))
    residual=sp.Tuple(*(l+w**2/c**2*e for l,e in zip(lap,field)))
    result=tuple(sp.srepr(e) for e in [harmonic,lap,residual])
    for e in result:_checked_parse(e)
    return result

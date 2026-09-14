"""Normalized symbolic Dirichlet interval modes."""
import ast
import json
import re
import sympy as sp
from sympy.simplify.fu import TR8
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


def witness_dirichlet_mode(width_srepr: AbstractScalar, mode_index_srepr: AbstractScalar,
                          phase_srepr: AbstractScalar) -> tuple[AbstractScalar, AbstractScalar,
                                                               AbstractScalar, AbstractScalar,
                                                               AbstractScalar, AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(6))


@register_atom(witness_dirichlet_mode)
def dirichlet_mode(width_srepr: str, mode_index_srepr: str, phase_srepr: str
                   ) -> tuple[str, str, str, str, str, str]:
    """Return wave, opposite_wave, wavenumber, derivative, second_derivative
    srepr strings and certificate_json for a unit-normalized Dirichlet mode.

    Guarded inputs: positive finite real width, positive integer mode index,
    finite real constant phase. Fixed real coordinate x is reserved. Parameters
    must not depend on x; conflicting symbol assumptions are rejected. Parsed
    floats become exact binary-value rationals before arithmetic. General
    symbolic parameters with provable domains are retained.

    psi=sqrt(2/W)*exp(I*phase)*sin(n*pi*x/W), on [0,W]. Interior derivatives
    solve -psi''=k² psi; endpoint values vanish and integral |psi|² is one.
    The opposite sign is the same eigenspace. Phase zero/pi recovers both
    source real branches. Width carries length, psi carries L^(-1/2), phase
    and index are dimensionless; caller establishes compatible units.
    No exterior derivative matching, finite-well, energy conversion, arbitrary
    boundary or completeness claim. Symbolic runtime, not a numeric sampler.
    """
    parsed = [_checked_parse(v) for v in (width_srepr, mode_index_srepr, phase_srepr)]
    known = {}
    for value in parsed:
        if not isinstance(value, sp.Expr) or value.is_commutative is not True:
            raise ValueError('Commutative scalar parameters required')
        for symbol in value.free_symbols:
            if symbol.name == 'x':
                raise ValueError('Coordinate x is reserved; parameters must be constant')
            if symbol.name in known and known[symbol.name] != symbol:
                raise ValueError('Conflicting symbol assumptions')
            known[symbol.name] = symbol
    width, n, phase = [v.xreplace({f: sp.Rational(f) for f in v.atoms(sp.Float)}).doit() for v in parsed]
    if any(v.is_finite is not True or v.is_real is not True for v in [width, n, phase]):
        raise ValueError('Finite real parameters required')
    if width.is_positive is not True or n.is_positive is not True or n.is_integer is not True:
        raise ValueError('Positive width and positive integer mode index required')
    x = sp.Symbol('x', real=True)
    k = n*sp.pi/width
    amplitude = sp.sqrt(2/width)*sp.exp(sp.I*phase)
    wave = amplitude*sp.sin(k*x)
    derivative = amplitude*k*sp.cos(k*x)
    second = -k*k*wave
    density = 2*sp.sin(k*x)**2/width
    primitive = x/width-sp.sin(2*k*x)/(2*k*width)
    checks = [(sp.diff(wave, x), derivative), (sp.diff(wave, x, 2), second),
              (-second, k*k*wave), (wave.subs(x, 0), sp.Integer(0)),
              (wave.subs(x, width), sp.Integer(0)), (sp.diff(primitive, x), density),
              (primitive.subs(x, width)-primitive.subs(x, 0), sp.Integer(1))]
    if any(sp.cancel(TR8(lhs-rhs)) != 0 for lhs, rhs in checks):
        raise ValueError('Dirichlet boundary/normalization certificate failed')
    encoded = [sp.srepr(v) for v in [wave, -wave, k, derivative, second]]
    for value in encoded:
        _checked_parse(value)
    certificate = dict(schema='sciona.normalized-dirichlet-mode.v1',
        inputs=dict(width_srepr=sp.srepr(width), mode_index_srepr=sp.srepr(n), phase_srepr=sp.srepr(phase)),
        coordinate_srepr=sp.srepr(x), eigenvalue_srepr=sp.srepr(k*k),
        density_srepr=sp.srepr(density), density_antiderivative_srepr=sp.srepr(primitive),
        identities=[dict(lhs_srepr=sp.srepr(lhs), rhs_srepr=sp.srepr(rhs)) for lhs, rhs in checks],
        domain='0<=x<=width; differential equation and derivatives apply in the interior. No exterior extension.',
        source_ast_parity=False)
    return (*encoded, json.dumps(certificate, sort_keys=True))


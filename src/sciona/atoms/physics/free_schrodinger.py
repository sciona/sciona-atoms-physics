"""Exact symbolic three-dimensional free-particle plane waves."""
import ast
import json
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


def witness_free_schrodinger(mass_srepr: AbstractScalar, hbar_srepr: AbstractScalar,
                            momentum_srepr: AbstractScalar, amplitude_srepr: AbstractScalar
                            ) -> tuple[AbstractScalar, AbstractScalar, AbstractScalar,
                                       AbstractScalar, AbstractScalar, AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(6))


@register_atom(witness_free_schrodinger)
def free_schrodinger(mass_srepr: str, hbar_srepr: str, momentum_srepr: str,
                    amplitude_srepr: str) -> tuple[str, str, str, str, str, str]:
    """Return wave_srepr, energy_srepr, gradient_json, laplacian_srepr,
    time_derivative_srepr and certificate_json for a free plane wave.

    Guarded serialized symbolic inputs: positive finite real mass and hbar,
    Tuple of three finite real momentum components, finite complex amplitude.
    All are constants independent of fixed real coordinates x,y,z,t; these
    names are reserved. General parameters with provable assumptions, exact
    constants, zero momentum and zero amplitude are supported. Floats are
    converted to exact rationals representing their parsed binary values before
    arithmetic. Conflicting assumptions for one symbol name are rejected.

    Wave = A*exp(I*(p dot r-p dot p*t/(2*m))/hbar), U=0. Derivatives and kinetic
    Hamiltonian are checked symbolically and serialized in the certificate.
    Caller establishes compatible units: SI mass, action and momentum, amplitude
    in L^(-3/2). This dimension convention does not normalize an infinite-space
    plane wave. No potential, boundary, spin or relativistic model; no arbitrary
    wavefunction or numerical PDE solver. Symbolic dependencies required.
    """
    parsed = [_checked_parse(s) for s in (mass_srepr, hbar_srepr, momentum_srepr, amplitude_srepr)]
    if not isinstance(parsed[2], sp.Tuple) or len(parsed[2]) != 3:
        raise ValueError('Three-component momentum Tuple required')
    components = [parsed[0], parsed[1], *parsed[2], parsed[3]]
    known = {}
    for component in components:
        if not isinstance(component, sp.Expr) or component.is_commutative is not True:
            raise ValueError('Commutative scalar components required')
        for symbol in component.free_symbols:
            if symbol.name in {'x', 'y', 'z', 't'}:
                raise ValueError('Coordinate names are reserved; parameters must be constant')
            if symbol.name in known and known[symbol.name] != symbol:
                raise ValueError('Conflicting symbol assumptions')
            known[symbol.name] = symbol
    exact = [c.xreplace({f: sp.Rational(f) for f in c.atoms(sp.Float)}).doit() for c in components]
    m, hbar, px, py, pz, amplitude = exact
    if any(c.is_finite is not True or c.is_real is not True for c in exact[:5]):
        raise ValueError('Finite real mass, hbar and momentum required')
    if m.is_positive is not True or hbar.is_positive is not True:
        raise ValueError('Positive mass and hbar required')
    if amplitude.is_finite is not True or amplitude.is_complex is not True:
        raise ValueError('Finite complex amplitude required')
    x, y, z, t = sp.symbols('x y z t', real=True)
    coordinates, momentum = (x, y, z), (px, py, pz)
    p2 = sum(p*p for p in momentum)
    energy = p2/(2*m)
    wave = amplitude*sp.exp(sp.I*(sum(p*q for p, q in zip(momentum, coordinates))-energy*t)/hbar)
    gradient = [sp.I*p*wave/hbar for p in momentum]
    laplacian = -p2*wave/hbar**2
    time_derivative = -sp.I*energy*wave/hbar
    action = energy*wave
    checks = [(sp.diff(wave, q), value) for q, value in zip(coordinates, gradient)]
    checks += [(sum(sp.diff(wave, q, 2) for q in coordinates), laplacian),
               (sp.diff(wave, t), time_derivative),
               (-hbar**2*laplacian/(2*m), action), (sp.I*hbar*time_derivative, action)]
    if any(sp.simplify(lhs-rhs) != 0 for lhs, rhs in checks):
        raise ValueError('Symbolic free-wave certificate failed')
    encoded = [sp.srepr(value) for value in [wave, energy, *gradient, laplacian, time_derivative, action]]
    for value in encoded:
        _checked_parse(value)
    certificate = dict(schema='sciona.free-schrodinger-plane-wave.v1',
        inputs=dict(mass_srepr=sp.srepr(m), hbar_srepr=sp.srepr(hbar),
                    momentum_srepr=sp.srepr(sp.Tuple(*momentum)), amplitude_srepr=sp.srepr(amplitude)),
        coordinates_srepr=[sp.srepr(q) for q in (*coordinates, t)],
        hamiltonian_action_srepr=sp.srepr(action),
        identities=[dict(lhs_srepr=sp.srepr(lhs), rhs_srepr=sp.srepr(rhs)) for lhs, rhs in checks],
        physical_regime='Free nonrelativistic scalar particle, constant parameters, U=0; no boundary or normalized-state claim.',
        source_ast_parity=False)
    return (encoded[0], encoded[1], json.dumps(encoded[2:5]), encoded[5], encoded[6],
            json.dumps(certificate, sort_keys=True))

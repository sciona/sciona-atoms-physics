"""Complete hyperbolic identities and exponential-definition certificate."""
import json
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



def _derive():
    x = sp.Symbol('x', real=True)
    p, q = sp.exp(x), sp.exp(-x)
    s, c = (p-q)/2, (p+q)/2
    S, C, T, H = sp.sinh(x), sp.cosh(x), sp.tanh(x), sp.sech(x)
    eq = lambda lhs, rhs: sp.Eq(lhs, rhs, evaluate=False)
    return [eq(S**2, s**2), eq(C**2, c**2),
            eq(C**2-S**2, c**2-s**2),
            eq(C**2-S**2, (sp.exp(2*x)+2+sp.exp(-2*x)-(sp.exp(2*x)-2+sp.exp(-2*x)))/4),
            eq(C**2-S**2, 1),
            eq(sp.sin(sp.I*x), (q-p)/(2*sp.I)),
            eq(sp.sin(sp.I*x), sp.I*S),
            eq(sp.I*S, (q-p)/(2*sp.I)),
            eq(sp.cos(sp.I*x), (q+p)/2),
            eq(sp.cos(sp.I*x), C),
            eq(H, 2/(p+q)), eq(T, s/C), eq(T, (p-q)/(p+q)),
            eq(T**2, (p-q)**2/(p+q)**2),
            eq(H**2, 4/(p+q)**2),
            eq(H**2+T**2, (4+(p-q)**2)/(p+q)**2),
            eq(H**2+T**2, (sp.exp(2*x)+2+sp.exp(-2*x))/(p+q)**2),
            eq(H**2+T**2, 1)]


def _verify(proof):
    if proof != _derive():
        raise ValueError('Reviewed hyperbolic reconstruction changed')
    x = sp.Symbol('x', real=True)
    order = [1, 2, 3, 4, 5, 6, 8, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    for number in order:
        equation = proof[number-1]
        if sp.simplify((equation.lhs-equation.rhs).rewrite(sp.exp)) != 0:
            raise ValueError('Exponential-definition residual failed at step '+str(number))
    # A positive exponential and its reciprocal establish a nonzero denominator
    # for every real x. This is false for general complex inputs.
    if (sp.exp(x)+sp.exp(-x)).is_positive is not True:
        raise ValueError('Quotient domain not established')
    z = sp.Symbol('z', complex=True, finite=True)
    sine = (sp.exp(sp.I*z)-sp.exp(-sp.I*z))/(2*sp.I)
    cosine = (sp.exp(sp.I*z)+sp.exp(-sp.I*z))/2
    checks = [sp.diff(sine, z)-cosine, sp.diff(cosine, z)+sine,
              sine.subs(z, 0), cosine.subs(z, 0)-1,
              sine.subs(z, sp.I*x)-sp.I*sp.sinh(x).rewrite(sp.exp),
              cosine.subs(z, sp.I*x)-sp.cosh(x).rewrite(sp.exp)]
    if any(sp.simplify(v) != 0 for v in checks):
        raise ValueError('Complex exponential definitions failed')
    return dict(
                source_steps_reviewed=18, source_ast_parity=False,
                reconstructed_steps_validated=18, replay_order=order,
                complex_definition_checks=6, denominator_positive=True,
                assumptions=['Finite real dimensionless x; I is the mathematical imaginary unit.',
                             'Entire complex sine/cosine and hyperbolic exponential definitions.'],
                prerequisite_scope='Complex exponential definitions are checked directly; no substitution into a real-only Euler certificate.',
                limitations=['No literal uncorrected source AST replay.',
                             'Tanh and sech quotients are not globally defined for complex x; real domain is deliberate.',
                             'Algebraic certificates do not promise stable evaluation by subtracting rounded cosh/sinh squares.'])


def witness_hyperbolic_identities(argument_srepr: AbstractScalar) -> tuple[AbstractScalar, AbstractScalar, AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_hyperbolic_identities)
def hyperbolic_identities(argument_srepr: str) -> tuple[str, str, str]:
    """Return functions_json, identities_json and certificate_json.

    Input is guarded srepr for a provably finite real commutative dimensionless
    scalar. Exact constants and general symbolic real expressions are supported;
    caller establishes units. Six named function ASTs include sinh, cosh, tanh,
    sech, sin(I*x) and cos(I*x). All18 reconstructed identity pairs are returned
    at the supplied argument along with a self-contained generic certificate.
    Mathematical I is used; quotient denominators are positive on the real line.
    Complex sine/cosine exponential definitions are checked directly, without
    substituting complex inputs into a real-only Euler theorem. No arbitrary
    complex-input quotient, numeric stability or literal source-parity claim.
    Symbolic extra required; no float64 evaluation of cancellation-prone squares.
    """
    argument = _checked_parse(argument_srepr)
    if not isinstance(argument, sp.Expr) or argument.is_commutative is not True or argument.is_real is not True or argument.is_finite is not True:
        raise ValueError('Provably finite real scalar required')
    symbols = {}
    for symbol in argument.free_symbols:
        if symbol.name in symbols and symbols[symbol.name] != symbol:
            raise ValueError('Conflicting symbol assumptions')
        symbols[symbol.name] = symbol
    steps = _derive()
    verified = _verify(steps)
    x = sp.Symbol('x', real=True)
    functions = {name: sp.srepr(function(argument, evaluate=False)) for name, function in
                 [('sinh', sp.sinh), ('cosh', sp.cosh), ('tanh', sp.tanh), ('sech', sp.sech)]}
    functions.update(sin_imaginary=sp.srepr(sp.sin(sp.I*argument, evaluate=False)),
                     cos_imaginary=sp.srepr(sp.cos(sp.I*argument, evaluate=False)))
    identities = [dict(step=i+1, lhs_srepr=sp.srepr(eq.lhs.xreplace({x: argument})),
                       rhs_srepr=sp.srepr(eq.rhs.xreplace({x: argument}))) for i, eq in enumerate(steps)]
    for encoded in list(functions.values())+[v[k] for v in identities for k in ['lhs_srepr', 'rhs_srepr']]:
        _checked_parse(encoded)
    certificate = dict(schema='sciona.hyperbolic-exponential-identities.v1',
                       argument_srepr=sp.srepr(argument), steps=[sp.srepr(e) for e in steps],
                       functions=functions, specialized_identities=identities, verification=verified)
    return tuple(json.dumps(v, sort_keys=True) for v in [functions, identities, certificate])

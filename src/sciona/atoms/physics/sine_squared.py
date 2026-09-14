"""Sine-squared half-angle identity and symbolic certificate."""
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



def eq(a,b):return sp.Eq(a,b,evaluate=False)


def _derive():
    x=sp.Symbol('x',real=True);s,c=sp.sin(x),sp.cos(x)
    doubled=eq(sp.exp(2*sp.I*x),sp.cos(2*x)+sp.I*sp.sin(2*x))
    product=eq(sp.exp(2*sp.I*x),(c+sp.I*s)**2)
    expanded=eq(product.lhs,sp.expand(product.rhs))
    comparison=eq(doubled.rhs,expanded.rhs)
    real_parts=eq(sp.re(comparison.lhs),sp.re(comparison.rhs))
    added=eq(real_parts.lhs+s**2,sp.expand(real_parts.rhs+s**2))
    pythagorean=eq(c**2,1-s**2)
    swapped=eq(added.rhs,added.lhs)
    combined=eq(swapped.rhs,pythagorean.rhs)
    subtracted=eq(sp.expand(combined.lhs-s**2),sp.expand(combined.rhs-s**2))
    add_twice=eq(subtracted.lhs+2*s**2,sp.expand(subtracted.rhs+2*s**2))
    rearranged=eq(sp.expand(add_twice.lhs-sp.cos(2*x)),add_twice.rhs-sp.cos(2*x))
    answer=eq(rearranged.lhs/2,rearranged.rhs/2)
    return (doubled,comparison,product,expanded,real_parts,added,pythagorean,
            swapped,combined,subtracted,add_twice,rearranged,answer)


def witness_sine_squared(angle_srepr: AbstractScalar) -> tuple[AbstractScalar,AbstractScalar,AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_sine_squared)
def sine_squared(angle_srepr: str) -> tuple[str,str,str]:
    """Return sin(angle)^2, its half-angle AST, and a JSON proof certificate.

    Guarded srepr input must describe a provably finite real commutative scalar
    angle in dimensionless radians. Exact constants and general symbolic real
    expressions accepted. Caller establishes units/assumptions. Symbolic extra
    required. No float64 evaluation, principal-square-root sign inference, or
    arbitrary complex-angle claim. Symbolic Float literals describe the supplied
    approximation; use exact constants for exact numerical identities.

    Retains all13reconstructed source transitions, with Euler product-rule and
    Pythagorean prerequisites. Source dependency order corrected to1,3,4,2,...13.
    Independent endpoint checks use y third derivative+4*y first derivative=0
    and matching initial data (0,0,2); constant-coefficient linear ODE uniqueness
    proves equality on the real line. Source symbol/feed mistakes corrected;
    literal source AST parity is not claimed. No numerical cancellation claim
    for evaluating the returned half-angle expression in other software.
    """
    angle=_checked_parse(angle_srepr)
    if not isinstance(angle,sp.Expr) or angle.is_commutative is not True or angle.is_real is not True or angle.is_finite is not True:
        raise ValueError('Provably finite real scalar angle required')
    identities={}
    for symbol in angle.free_symbols:
        if symbol.name in identities and identities[symbol.name]!=symbol:
            raise ValueError('Conflicting symbol assumptions')
        identities[symbol.name]=symbol
    x=sp.Symbol('x',real=True)
    y=sp.cos(x)+sp.I*sp.sin(x)
    euler_residual=sp.expand(sp.diff(y,x)-sp.I*y)
    product=sp.expand(sp.diff(sp.exp(-sp.I*x)*y,x))
    norm=sp.cos(x)**2+sp.sin(x)**2
    if euler_residual!=0 or product!=0 or y.subs(x,0)!=1 or sp.expand(sp.diff(norm,x))!=0 or norm.subs(x,0)!=1:
        raise ValueError('Euler/Pythagorean prerequisites failed')
    steps=_derive()
    differential=[]
    for side in (steps[-1].lhs,steps[-1].rhs):
        residual=sp.expand(sp.diff(side,x,3)+4*sp.diff(side,x))
        initial=[sp.diff(side,x,j).subs(x,0) for j in range(3)]
        if residual!=0 or initial!=[0,0,2]:raise ValueError('Endpoint ODE certificate failed')
        differential.append(dict(residual=sp.srepr(residual),initial_values=[str(v) for v in initial]))
    # Keep structure unevaluated: no rounded cosine subtraction inside provider.
    left=sp.srepr(sp.Pow(sp.sin(angle,evaluate=False),2,evaluate=False))
    right=sp.srepr(sp.Mul(sp.Rational(1,2),sp.Add(1,-sp.cos(2*angle,evaluate=False),evaluate=False),evaluate=False))
    for encoded in (left,right):_checked_parse(encoded)
    certificate=dict(schema='sciona.sine-squared-ode.v1',angle_srepr=sp.srepr(angle),
        steps=[sp.srepr(s) for s in steps],execution_order=[1,3,4,2,5,6,7,8,9,10,11,12,13],
        euler_ode_residual=sp.srepr(euler_residual),integrating_factor_derivative=sp.srepr(product),
        differential_certificates=differential,
        theorem='Uniqueness for y third derivative+4*y first derivative=0 with three matching initial values on the real line.',
        specialized_lhs_srepr=left,specialized_rhs_srepr=right,
        source_ast_parity=False,sine_sign_inferred=False)
    return left,right,json.dumps(certificate,sort_keys=True)

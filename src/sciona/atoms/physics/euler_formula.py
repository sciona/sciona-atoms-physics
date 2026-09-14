"""General real-angle Euler formula with branch-free ODE certificate."""
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



def witness_euler_formula(angle_srepr: AbstractScalar) -> tuple[AbstractScalar,AbstractScalar,AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_euler_formula)
def euler_formula(angle_srepr: str) -> tuple[str,str,str]:
    """Return exponential AST, trigonometric AST and JSON proof certificate.

    Input a guarded srepr of a provably finite real commutative scalar angle in
    radians (dimensionless). Symbolic real expressions and exact constants are
    accepted; undecidable realness/finiteness rejected. The result is a symbolic
    identity, not a float64 numerical approximation or arbitrary complex-angle
    extension. Caller establishes units and symbolic assumptions.

    Certificate uses y=cos(x)+i sin(x), y'=iy and y(0)=1; the product rule yields
    (exp(-ix)y)'=0. Fundamental theorem of calculus on the connected real line
    gives exp(-ix)y=1. This uses no complex-log branch or Euler-formula rewrite
    in its derivative checks. Substitution specializes the global identity to
    the supplied angle. Source malformed logarithm steps are not certified.
    Requires symbolic extra; no throughput claim.
    """
    angle=_checked_parse(angle_srepr)
    if not isinstance(angle,sp.Expr) or angle.is_commutative is not True or angle.is_real is not True or angle.is_finite is not True:
        raise ValueError('Provably finite real scalar angle required')
    identities={}
    for symbol in angle.free_symbols:
        if symbol.name in identities and identities[symbol.name]!=symbol:
            raise ValueError('Conflicting symbol assumptions')
        identities[symbol.name]=symbol
    x=sp.Symbol('proof_angle',real=True)
    y=sp.cos(x)+sp.I*sp.sin(x)
    derivative=sp.expand(sp.diff(y,x)-sp.I*y)
    product=sp.expand(sp.diff(sp.exp(-sp.I*x)*y,x))
    if derivative!=0 or product!=0 or y.subs(x,0)!=1:
        raise ValueError('General ODE proof failed')
    exponential=sp.exp(sp.I*angle);trigonometric=sp.cos(angle)+sp.I*sp.sin(angle)
    left,right=sp.srepr(exponential),sp.srepr(trigonometric)
    for encoded in [left,right]:_checked_parse(encoded)
    certificate=dict(schema='sciona.euler-formula-ode.v1',angle_srepr=sp.srepr(angle),
        general_variable_srepr=sp.srepr(x),ode_residual=sp.srepr(derivative),initial_value=1,
        integrating_factor_derivative=sp.srepr(product),
        theorem='A differentiable function with zero derivative on the connected real line is constant.',
        normalization='exp(-i*0)*y(0)=1',conclusion='exp(i*x)=cos(x)+i*sin(x) for real x',
        specialized_lhs_srepr=left,specialized_rhs_srepr=right,uses_complex_log=False)
    return left,right,json.dumps(certificate,sort_keys=True)

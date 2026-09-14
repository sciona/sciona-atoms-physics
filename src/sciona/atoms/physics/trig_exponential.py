"""Sine and cosine exponential forms with checked Euler premise."""
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



def witness_trig_exponential(angle_srepr: AbstractScalar) -> tuple[AbstractScalar,AbstractScalar,AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_trig_exponential)
def trig_exponential(angle_srepr: str) -> tuple[str,str,str]:
    """Return cosine exponential AST, sine exponential AST and JSON certificate.

    Input guarded srepr of a provably finite real scalar dimensionless angle in
    radians. Exact constants and symbolic real expressions accepted; undecidable
    assumptions rejected. Outputs are (exp(ix)+exp(-ix))/2 and
    (exp(ix)-exp(-ix))/(2i), with proof certificate specialized to the input.
    No numerical approximation, complex-angle or unit-inference claim.

    Euler premise is independently checked by product-rule ODE residual and
    initial value y(0)=1 on connected real line. Two linear equations then yield
    both inverse representations, without dividing by sin/cos or using a complex
    logarithm. Requires symbolic extra. Caller establishes units and assumptions.
    """
    angle=_checked_parse(angle_srepr)
    if not isinstance(angle,sp.Expr) or angle.is_commutative is not True or angle.is_real is not True or angle.is_finite is not True:
        raise ValueError('Provably finite real scalar angle required')
    identities={}
    for symbol in angle.free_symbols:
        if symbol.name in identities and identities[symbol.name]!=symbol:raise ValueError('Conflicting assumptions')
        identities[symbol.name]=symbol
    x=sp.Symbol('proof_angle',real=True);y=sp.cos(x)+sp.I*sp.sin(x)
    ode=sp.expand(sp.diff(y,x)-sp.I*y)
    factor=sp.expand(sp.diff(sp.exp(-sp.I*x)*y,x))
    if ode!=0 or factor!=0 or y.subs(x,0)!=1:raise ValueError('Euler premise failed')
    p,n,c,s=sp.symbols('positive negative cosine sine')
    cosine=(p+n)/2;sine=(p-n)/(2*sp.I)
    if sp.expand(cosine+sp.I*sine-p)!=0 or sp.expand(cosine-sp.I*sine-n)!=0:
        raise ValueError('Linear inverse failed')
    positive=sp.exp(sp.I*angle);negative=sp.exp(-sp.I*angle)
    outputs=[sp.srepr((positive+negative)/2),sp.srepr((positive-negative)/(2*sp.I))]
    for out in outputs:_checked_parse(out)
    certificate=dict(schema='sciona.trig-exponential.v1',angle_srepr=sp.srepr(angle),
        euler_ode_residual=sp.srepr(ode),integrating_factor_derivative=sp.srepr(factor),initial_value=1,
        premise_theorem='Zero derivative on connected real line and initial value fix the integrating factor to1.',
        cosine_solution=sp.srepr(cosine),sine_solution=sp.srepr(sine),
        linear_system_residuals=['Integer(0)','Integer(0)'],divisors=['Integer(2)',sp.srepr(2*sp.I)],
        cosine_exponential_srepr=outputs[0],sine_exponential_srepr=outputs[1],uses_complex_log=False)
    return *outputs,json.dumps(certificate,sort_keys=True)

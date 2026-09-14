"""Exact finite-dimensional Hermitian eigenstate overlap calculation."""
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



def witness_eigenstate_orthogonality(operator_srepr: AbstractScalar, initial_state_srepr: AbstractScalar,
                                     final_state_srepr: AbstractScalar, initial_eigenvalue_srepr: AbstractScalar,
                                     final_eigenvalue_srepr: AbstractScalar) -> tuple[AbstractScalar,AbstractScalar,AbstractScalar]:
    return tuple(AbstractScalar(dtype='str') for _ in range(3))


@register_atom(witness_eigenstate_orthogonality)
def eigenstate_orthogonality(operator_srepr: str, initial_state_srepr: str, final_state_srepr: str,
                            initial_eigenvalue_srepr: str, final_eigenvalue_srepr: str) -> tuple[str,str,str]:
    """Return srepr overlap u†v, matrix element u†Av and (b-a)u†v.

    A is a nonempty square nested Tuple; u,v are matching nonempty Tuples.
    Entries are finite commutative scalar expressions. Eigenvalues a,b must be
    provably finite real. Verify A†=A, Au=au, Av=bv and nonzero states exactly
    by symbolic simplification. Undecidable conditions are rejected; no numeric
    tolerance silently establishes a mathematical premise. Prefer exact rational
    and algebraic inputs. States need not be normalized. Complex adjoints apply.

    Equal eigenvalues are accepted and may yield nonzero overlap. The third
    output is computed from the actual overlap; zero overlap follows only for
    distinct eigenvalues. No orthogonalization, eigensolver or infinite-dimensional
    operator claim. An orthonormal finite basis and consistent caller-established
    units are required: dimensionless vector components, common units for A,a,b
    and matrix element. Requires symbolic extra. Bounded guarded srepr parsing.
    """
    matrix,u,v,a,b=map(_checked_parse,[operator_srepr,initial_state_srepr,final_state_srepr,
                                    initial_eigenvalue_srepr,final_eigenvalue_srepr])
    if not isinstance(matrix,sp.Tuple) or not matrix:
        raise ValueError('Nonempty nested Tuple matrix required')
    n=len(matrix)
    if any(not isinstance(row,sp.Tuple) or len(row)!=n for row in matrix):
        raise ValueError('Square matrix required')
    if any(not isinstance(state,sp.Tuple) or len(state)!=n for state in [u,v]):
        raise ValueError('Matching state Tuples required')
    entries=[entry for row in matrix for entry in row]+list(u)+list(v)+[a,b]
    if any(not isinstance(e,sp.Expr) or e.is_commutative is not True or e.is_finite is not True for e in entries):
        raise ValueError('Provably finite scalar entries required')
    identities={}
    for e in entries:
        for symbol in e.free_symbols:
            if symbol.name in identities and identities[symbol.name]!=symbol:
                raise ValueError('Conflicting symbol assumptions')
            identities[symbol.name]=symbol
    if a.is_real is not True or b.is_real is not True:
        raise ValueError('Real eigenvalues required')
    A=sp.ImmutableMatrix([list(row) for row in matrix]);u=sp.ImmutableMatrix(u);v=sp.ImmutableMatrix(v)
    def zero_matrix(m): return all(sp.simplify(e)==0 for e in m)
    if not zero_matrix(A.H-A): raise ValueError('Hermitian operator required')
    if any(not any(sp.simplify(e).is_zero is False for e in state) for state in [u,v]):
        raise ValueError('Provably nonzero eigenstates required')
    if not zero_matrix(A*u-a*u) or not zero_matrix(A*v-b*v):
        raise ValueError('Both eigenvector equations must hold exactly')
    overlap=sp.simplify((u.H*v)[0]);element=sp.simplify((u.H*A*v)[0])
    product=sp.simplify((b-a)*overlap)
    if product!=0 or sp.simplify(element-a*overlap)!=0 or sp.simplify(element-b*overlap)!=0:
        raise ValueError('Eigenstate identity could not be established')
    result=tuple(sp.srepr(e) for e in [overlap,element,product])
    for e in result:_checked_parse(e)
    return result

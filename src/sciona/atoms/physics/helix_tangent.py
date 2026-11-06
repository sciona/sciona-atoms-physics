"""Reusable helix construction and oriented tangent geometry.

Arithmetic adapted from edwinst/trackml_solution (BSD-2-Clause).
Copyright and license: ../particle_tracking/source_tracking/solution_LICENSE.source.
Regularization controls and coordinate units are supplied by the caller.
"""
import numpy as np
from sciona.ghost.registry import register_atom


def concrete_only(*args, **kwargs):
    raise ValueError('Concrete finite helix arrays required')


def _array(value, shape):
    a = np.asarray(value)
    if a.dtype != np.float64 or a.shape != shape or not np.isfinite(a).all():
        raise ValueError('Aligned finite float64 arrays required')
    return a


def _points(value):
    a = np.asarray(value)
    if a.ndim != 2 or a.shape[1] != 3:
        raise ValueError('Point matrix (N,3) required')
    return _array(a,a.shape)


@register_atom(concrete_only)
def construct_helix_from_tangent(points: np.ndarray, tangents: np.ndarray, pitch: np.ndarray,
                                 minimum_axial: float, maximum_scale: float
                                 ) -> tuple[np.ndarray, np.ndarray]:
    """Construct transverse centers and radii with explicit regulation.

Points and tangents are aligned finite float64 (N,3); pitch is (N,), in the
same caller-defined length unit as points. Tangents are dimensionless and
need not be unit vectors. minimum_axial is positive and dimensionless;
maximum_scale is positive with length units. The axial tangent component is
floored in magnitude (zero uses positive sign), then -pitch/(2*pi*axial) is
clipped to maximum_scale. Regulation can change the input tangent direction;
rescaling tangents can change regulated results. Returns centers (N,2) and
nonnegative radii (N,). Empty batches allowed. No detector policy is embedded.
Nonfinite intermediates reject before clipping can conceal overflow.
"""
    p = _points(points); n = len(p)
    t = _array(tangents,p.shape); h = _array(pitch,(n,))
    for control in (minimum_axial,maximum_scale):
        if isinstance(control,(bool,np.bool_)) or not isinstance(control,(int,float,np.integer,np.floating)) or not np.isfinite(control) or control <= 0:
            raise ValueError('Positive finite real regulation controls required')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            axial = np.where(np.abs(t[:,2]) >= minimum_axial, t[:,2], minimum_axial*(1-2*(t[:,2]<0)))
            scale = -h/(2*np.pi*axial)
            large = np.abs(scale)>maximum_scale
            scale[large] = np.sign(scale[large])*maximum_scale
            xm = p[:,0]+t[:,1]*scale
            ym = p[:,1]-t[:,0]*scale
            radius = np.sqrt(np.square(p[:,0]-xm)+np.square(p[:,1]-ym))
    except FloatingPointError as exc:
        raise ValueError('Nonfinite helix construction arithmetic') from exc
    center=np.column_stack((xm,ym))
    if not np.isfinite(center).all() or not np.isfinite(radius).all():
        raise ValueError('Nonfinite helix construction output')
    return center,radius


@register_atom(concrete_only)
def oriented_helix_tangent(points: np.ndarray, centers: np.ndarray, radius: np.ndarray,
                           pitch: np.ndarray, axial_direction: np.ndarray) -> np.ndarray:
    """Evaluate an oriented tangent using supplied helix geometry.

Finite float64 points (N,3), centers (N,2), and vectors radius, pitch and
axial_direction (N,) must align. Coordinates, nonnegative radii and signed
pitch per revolution share caller-defined length units. Caller must supply
points on each transverse circle; only then is the result a unit vector.
Only the sign of axial_direction is used. Its product with pitch must be
finite and nonzero. Empty batches allowed; nonfinite arithmetic rejects.
Returns float64 (N,3). No unit normalization of inconsistent geometry,
coordinate conversion, detector topology or physical field model is supplied.
"""
    p=_points(points); n=len(p)
    c=_array(centers,(n,2)); r=_array(radius,(n,)); h=_array(pitch,(n,)); z=_array(axial_direction,(n,))
    if np.any(r<0):raise ValueError('Nonnegative radius required')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            product=z*h
            if np.any(product==0):raise ValueError('Nonzero representable direction times pitch required')
            sign=np.sign(product); step=h/(2*np.pi)
            norm=sign*np.sqrt(np.square(r)+np.square(step))
            dx=p[:,0]-c[:,0]; dy=p[:,1]-c[:,1]
            result=np.stack((-dy,dx,step),axis=1)/norm[:,None]
    except FloatingPointError as exc:
        raise ValueError('Nonfinite tangent arithmetic') from exc
    if not np.isfinite(result).all():raise ValueError('Nonfinite tangent output')
    return result

"""Brewster incidence and complementary refraction angles."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_brewster_angle(incident_index: AbstractArray, transmitted_index: AbstractArray) -> tuple[AbstractArray,AbstractArray]:
    if incident_index.shape!=transmitted_index.shape:raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=incident_index.shape,dtype='float64') for _ in range(2))


@register_atom(witness_brewster_angle)
def brewster_angle(incident_index: NDArray[np.float64], transmitted_index: NDArray[np.float64]
                         ) -> tuple[NDArray[np.float64],NDArray[np.float64]]:
    """Return incidence and refraction angles in radians, measured from normal.

    Positive finite incident n1 and transmitted n2 refractive indices, identical
    nonempty real float64-compatible arrays including scalars. No broadcasting.
    Planar homogeneous isotropic lossless nonmagnetic interface; p-polarized
    reflection zero. No absorbing/complex-index or anisotropic-medium claim.
    Equal indices give pi/4 by complementary-angle convention; there is no unique
    Brewster angle because reflection vanishes for every incidence angle.

    Independent atan2(n2,n1) and atan2(n1,n2) in invocation-local450digit mpmath
    context avoid ratio overflow and rounded-complement cancellation. Outputs
    rounded independently to float64; tiny positive subnormals accepted, nonzero
    underflow to0 rejected. A near-grazing angle may round to float64 pi/2; this
    does not assert exact grazing incidence or exact Fresnel/Snell equality for
    rounded outputs. Use both returned angles instead of subtracting from pi/2.
    Accuracy evidence is not a universal correctly-rounded proof. Precision extra
    required; inputs preserved, no throughput claim.
    """
    import mpmath
    arrays=[]
    for value in [incident_index,transmitted_index]:
        raw=np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore',invalid='ignore'):a=raw.astype(np.float64,copy=True)
        if not np.isfinite(a).all() or np.any(a<=0):raise ValueError('Positive finite inputs required')
        arrays.append(a)
    if arrays[0].shape!=arrays[1].shape:raise ValueError('Identical shapes required without broadcasting')
    ctx=mpmath.mp.clone();ctx.dps=450
    outputs=[[],[]]
    for r,t in zip(arrays[0].flat,arrays[1].flat):
        mr,mt=ctx.mpf(float(r)),ctx.mpf(float(t))
        values=[ctx.atan2(mt,mr),ctx.atan2(mr,mt)]
        for bucket,value in zip(outputs,values):
            rounded=float(value)
            if not np.isfinite(rounded) or rounded<=0:raise ValueError('Output outside positive float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a,dtype=np.float64).reshape(arrays[0].shape) for a in outputs)

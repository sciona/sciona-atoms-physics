"""Conditional condensed-matter sound-speed scaling and approximation diagnostics."""
import numpy as np
from numpy.typing import NDArray
from sciona.ghost.abstract import AbstractArray
from sciona.ghost.registry import register_atom


def witness_sound_scale(atomic_mass: AbstractArray, fine_structure: AbstractArray,
                        light_speed: AbstractArray, electron_mass: AbstractArray,
                        proton_mass: AbstractArray, bulk_prefactor: AbstractArray,
                        shear_to_bulk: AbstractArray
                        ) -> tuple[AbstractArray, AbstractArray, AbstractArray, AbstractArray, AbstractArray]:
    if any(a.shape != atomic_mass.shape for a in (fine_structure, light_speed,
           electron_mass, proton_mass, bulk_prefactor, shear_to_bulk)):
        raise ValueError('Identical shapes required')
    return tuple(AbstractArray(shape=atomic_mass.shape, dtype='float64') for _ in range(5))


@register_atom(witness_sound_scale)
def sound_scale(atomic_mass: NDArray[np.float64], fine_structure: NDArray[np.float64],
                light_speed: NDArray[np.float64], electron_mass: NDArray[np.float64],
                proton_mass: NDArray[np.float64], bulk_prefactor: NDArray[np.float64],
                shear_to_bulk: NDArray[np.float64]
                ) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Return scaling estimate, A=1 scale, bulk model, longitudinal model, shear factor.

    A=atomic_mass is dimensionless m/mp (not mass in kg), A>=1. Positive alpha,
    c in m/s, me and mp in kg, bulk prefactor f>0, and shear_to_bulk=G/K>=0.
    Constants are caller supplied. All inputs must have identical nonempty real
    float64-compatible shapes; scalar inputs allowed, no broadcasting.

    With E modeled by the Rydberg scale me*(alpha*c)^2/2, m=A*mp,
    K=f*E/a^3 and rho=m/a^3, return respectively:
    alpha*c*sqrt(me/(2*A*mp)), alpha*c*sqrt(me/(2*mp)),
    sqrt(f)*estimate, sqrt(f*(1+4*G/(3*K)))*estimate,
    sqrt(1+4*G/(3*K)). The first four outputs have units m/s; the last is
    dimensionless. The factor2 corrects the source graph's final two equations.

    The A=1 scale bounds only the unit-prefactor, bulk-only scaling curve for
    A>=1. It does not bound arbitrary material speeds or the diagnostic models.
    Prefactor and shear outputs expose the approximations instead of silently
    assuming f=1 or G/K small. The Rydberg bonding-energy model remains an
    assumption, not an experimentally verified material property. No universal
    physical upper-bound, arbitrary-pressure, noncohesive-fluid or anisotropic
    elasticity claim. Callers establish the applicability of isotropic linear
    elasticity and this bonding-energy scale.

    Local450digit mpmath computes all positive outputs independently before
    float64 rounding, avoiding intermediate overflow. Inputs are copied and
    converted to float64 first. Nonzero subnormals allowed; underflow to zero or
    overflow rejects the entire call. Tests are not a universal correct-rounding
    proof. Requires the precision extra; no throughput claim.
    """
    import mpmath
    arrays = []
    for i, value in enumerate((atomic_mass, fine_structure, light_speed,
                              electron_mass, proton_mass, bulk_prefactor, shear_to_bulk)):
        raw = np.asarray(value)
        if not raw.size or raw.dtype.kind not in 'iuf':
            raise ValueError('Nonempty real inputs required')
        with np.errstate(over='ignore', invalid='ignore'):
            arr = raw.astype(np.float64, copy=True)
        if not np.isfinite(arr).all():
            raise ValueError('Finite inputs required')
        if (i == 0 and np.any(arr < 1)) or (0 < i < 6 and np.any(arr <= 0)) or (i == 6 and np.any(arr < 0)):
            raise ValueError('Require A>=1, positive constants/prefactor, nonnegative shear ratio')
        arrays.append(arr)
    if any(a.shape != arrays[0].shape for a in arrays[1:]):
        raise ValueError('Identical shapes required without broadcasting')
    ctx = mpmath.mp.clone()
    ctx.dps = 450
    outputs = [[], [], [], [], []]
    for row in zip(*(a.flat for a in arrays)):
        A, alpha, c, me, mp, f, g = (ctx.mpf(float(v)) for v in row)
        scale = alpha*c
        mass_ratio = me/(2*mp)
        shear_squared = 1+4*g/3
        values = (scale*ctx.sqrt(mass_ratio/A), scale*ctx.sqrt(mass_ratio),
                  scale*ctx.sqrt(f*mass_ratio/A),
                  scale*ctx.sqrt(f*mass_ratio*shear_squared/A), ctx.sqrt(shear_squared))
        for bucket, value in zip(outputs, values):
            rounded = float(value)
            if not np.isfinite(rounded) or rounded <= 0:
                raise ValueError('Output outside positive float64 range')
            bucket.append(rounded)
    return tuple(np.asarray(a, dtype=np.float64).reshape(arrays[0].shape) for a in outputs)

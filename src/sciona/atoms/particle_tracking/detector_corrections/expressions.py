"""Symbolic scalar relations for TrackML detector correction atoms."""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, METER, DimensionalSignature


LENGTH = METER
AREA = DimensionalSignature(L=2)

(
    x,
    y,
    z,
    r_xy,
    cyl_mean_r2,
    z_scale,
    x_scaled,
    xi,
    yi,
    zi,
    xi_corrected,
    yi_corrected,
    zi_corrected,
    ur_x,
    ur_y,
    uphi_x,
    uphi_y,
    hel_pitch,
    hel_p_abs,
    hel_r,
    curvature_radius,
    charge_sign,
    dp0_radial,
    dp1_azimuthal,
    dp0_z,
    sample_index,
) = sp.symbols(
    "x y z r_xy cyl_mean_r2 z_scale x_scaled xi yi zi xi_corrected "
    "yi_corrected zi_corrected ur_x ur_y uphi_x uphi_y hel_pitch hel_p_abs "
    "hel_r curvature_radius charge_sign dp0_radial dp1_azimuthal dp0_z "
    "sample_index"
)


DETECTOR_CORRECTIONS_BIBLIOGRAPHY = [
    "steiner2018trackml",
    "amrouche2019trackml",
]

COORDINATE_RESCALING_EXPR = sp.Eq(
    x_scaled,
    x * cyl_mean_r2 * z_scale / r_xy,
)
COORDINATE_RESCALING_DIM_MAP = {
    "coords": LENGTH,
    "x": LENGTH,
    "y": LENGTH,
    "z": LENGTH,
    "r_xy": LENGTH,
    "cyl_mean_r2": LENGTH,
    "z_scale": DIMENSIONLESS,
    "x_scaled": LENGTH,
}
COORDINATE_RESCALING_VARIABLES = {
    "coords": "input",
    "x": "input",
    "y": "input",
    "z": "input",
    "r_xy": "input",
    "cyl_mean_r2": "parameter",
    "z_scale": "parameter",
    "x_scaled": "output",
}
COORDINATE_RESCALING_VALIDITY_BOUNDS = {
    "r_xy": (0.0, None),
    "cyl_mean_r2": (0.0, None),
}

CAP_CORRECTION_EXPR = sp.Eq(
    xi_corrected,
    xi + (ur_x * dp0_radial + uphi_x * dp1_azimuthal) * charge_sign / hel_p_abs,
)
CAP_CORRECTION_DIM_MAP = {
    "xi": LENGTH,
    "yi": LENGTH,
    "xi_corrected": LENGTH,
    "yi_corrected": LENGTH,
    "ur_x": DIMENSIONLESS,
    "ur_y": DIMENSIONLESS,
    "uphi_x": DIMENSIONLESS,
    "uphi_y": DIMENSIONLESS,
    "hel_pitch": LENGTH,
    "hel_p_abs": LENGTH,
    "charge_sign": DIMENSIONLESS,
    "dp0_radial": AREA,
    "dp1_azimuthal": AREA,
}
CAP_CORRECTION_VARIABLES = {
    "xi": "input",
    "yi": "input",
    "xi_corrected": "output",
    "yi_corrected": "output",
    "ur_x": "parameter",
    "ur_y": "parameter",
    "uphi_x": "parameter",
    "uphi_y": "parameter",
    "hel_pitch": "input",
    "hel_p_abs": "parameter",
    "charge_sign": "parameter",
    "dp0_radial": "input",
    "dp1_azimuthal": "input",
}
CAP_CORRECTION_VALIDITY_BOUNDS = {
    "hel_p_abs": (0.0, None),
}

CYLINDER_CORRECTION_EXPR = sp.Eq(
    zi_corrected,
    zi + dp0_z * charge_sign / curvature_radius,
)
CYLINDER_CORRECTION_DIM_MAP = {
    "xi": LENGTH,
    "yi": LENGTH,
    "zi": LENGTH,
    "xi_corrected": LENGTH,
    "yi_corrected": LENGTH,
    "zi_corrected": LENGTH,
    "hel_r": LENGTH,
    "hel_pitch": LENGTH,
    "curvature_radius": LENGTH,
    "charge_sign": DIMENSIONLESS,
    "dp0_z": AREA,
    "dp1_azimuthal": AREA,
}
CYLINDER_CORRECTION_VARIABLES = {
    "xi": "input",
    "yi": "input",
    "zi": "input",
    "xi_corrected": "output",
    "yi_corrected": "output",
    "zi_corrected": "output",
    "hel_r": "input",
    "hel_pitch": "input",
    "curvature_radius": "parameter",
    "charge_sign": "parameter",
    "dp0_z": "input",
    "dp1_azimuthal": "input",
}
CYLINDER_CORRECTION_VALIDITY_BOUNDS = {
    "hel_r": (0.0, None),
    "curvature_radius": (0.0, None),
}

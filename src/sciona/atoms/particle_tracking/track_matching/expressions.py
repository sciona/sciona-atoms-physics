"""Symbolic scalar relations for TrackML track matching atoms."""

from __future__ import annotations

import sympy as sp

from sciona.ghost.dimensions import DIMENSIONLESS, METER, DimensionalSignature


LENGTH = METER
AREA = DimensionalSignature(L=2)
ANGLE = DIMENSIONLESS
COUNT = DIMENSIONLESS

(
    x0,
    y0,
    z0,
    hel_xm,
    hel_ym,
    hel_r,
    hel_pitch,
    hel_p,
    sign_uz,
    target_r2sqr,
    target_z,
    xi,
    yi,
    zi,
    dphi,
    d_theta,
    d_phi,
    bg_theta,
    bg_phi,
    e_theta,
    e_phi,
    de,
    cut,
    cut_factor,
    dist_trust,
    nhits,
    nfirst,
    nloss,
    loss_fraction,
    min_nhits,
    max_nloss,
    max_nrows,
) = sp.symbols(
    "x0 y0 z0 hel_xm hel_ym hel_r hel_pitch hel_p sign_uz target_r2sqr "
    "target_z xi yi zi dphi d_theta d_phi bg_theta bg_phi e_theta e_phi "
    "de cut cut_factor dist_trust nhits nfirst nloss loss_fraction "
    "min_nhits max_nloss max_nrows"
)


TRACK_MATCHING_BIBLIOGRAPHY = ["steiner2018trackml", "amrouche2019trackml"]

HELIX_CYLINDER_INTERSECTION_EXPR = sp.Eq(target_r2sqr, xi**2 + yi**2)
HELIX_CYLINDER_INTERSECTION_DIM_MAP = {
    "x0": LENGTH,
    "y0": LENGTH,
    "z0": LENGTH,
    "hel_xm": LENGTH,
    "hel_ym": LENGTH,
    "hel_r": LENGTH,
    "hel_pitch": LENGTH,
    "sign_uz": DIMENSIONLESS,
    "target_r2sqr": AREA,
    "xi": LENGTH,
    "yi": LENGTH,
    "zi": LENGTH,
    "dphi": ANGLE,
}
HELIX_CYLINDER_INTERSECTION_VARIABLES = {
    "x0": "input",
    "y0": "input",
    "z0": "input",
    "hel_xm": "input",
    "hel_ym": "input",
    "hel_r": "input",
    "hel_pitch": "input",
    "sign_uz": "parameter",
    "target_r2sqr": "input",
    "xi": "output",
    "yi": "output",
    "zi": "output",
    "dphi": "output",
}
HELIX_CYLINDER_INTERSECTION_VALIDITY_BOUNDS = {
    "hel_r": (0.0, None),
    "target_r2sqr": (0.0, None),
}

HELIX_CAP_INTERSECTION_EXPR = sp.Eq(dphi, (target_z - z0) / hel_p)
HELIX_CAP_INTERSECTION_DIM_MAP = {
    "x0": LENGTH,
    "y0": LENGTH,
    "z0": LENGTH,
    "hel_xm": LENGTH,
    "hel_ym": LENGTH,
    "hel_r": LENGTH,
    "hel_pitch": LENGTH,
    "hel_p": LENGTH,
    "target_z": LENGTH,
    "xi": LENGTH,
    "yi": LENGTH,
    "zi": LENGTH,
    "dphi": ANGLE,
}
HELIX_CAP_INTERSECTION_VARIABLES = {
    "x0": "input",
    "y0": "input",
    "z0": "input",
    "hel_xm": "input",
    "hel_ym": "input",
    "hel_r": "input",
    "hel_pitch": "input",
    "hel_p": "parameter",
    "target_z": "input",
    "xi": "output",
    "yi": "output",
    "zi": "output",
    "dphi": "output",
}
HELIX_CAP_INTERSECTION_VALIDITY_BOUNDS = {
    "hel_pitch": (0.0, None),
    "hel_p": (0.0, None),
}

BAYESIAN_NEIGHBOR_EVALUATION_EXPR = sp.Eq(
    de,
    sp.sqrt((d_theta / e_theta) ** 2 + (d_phi / e_phi) ** 2),
)
BAYESIAN_NEIGHBOR_EVALUATION_DIM_MAP = {
    "d_theta": ANGLE,
    "d_phi": ANGLE,
    "bg_theta": ANGLE,
    "bg_phi": ANGLE,
    "e_theta": ANGLE,
    "e_phi": ANGLE,
    "de": DIMENSIONLESS,
    "cut": DIMENSIONLESS,
    "cut_factor": DIMENSIONLESS,
    "dist_trust": DIMENSIONLESS,
}
BAYESIAN_NEIGHBOR_EVALUATION_VARIABLES = {
    "d_theta": "input",
    "d_phi": "input",
    "bg_theta": "input",
    "bg_phi": "input",
    "e_theta": "parameter",
    "e_phi": "parameter",
    "de": "output",
    "cut": "parameter",
    "cut_factor": "parameter",
    "dist_trust": "parameter",
}
BAYESIAN_NEIGHBOR_EVALUATION_VALIDITY_BOUNDS = {
    "e_theta": (0.0, None),
    "e_phi": (0.0, None),
    "cut_factor": (0.0, None),
    "dist_trust": (0.0, None),
}

GREEDY_TRACK_COMMIT_EXPR = sp.Eq(loss_fraction, nloss / nhits)
GREEDY_TRACK_COMMIT_DIM_MAP = {
    "nhits": COUNT,
    "nfirst": COUNT,
    "nloss": COUNT,
    "loss_fraction": DIMENSIONLESS,
    "min_nhits": COUNT,
    "max_nloss": COUNT,
    "max_nrows": COUNT,
}
GREEDY_TRACK_COMMIT_VARIABLES = {
    "nhits": "input",
    "nfirst": "input",
    "nloss": "output",
    "loss_fraction": "output",
    "min_nhits": "parameter",
    "max_nloss": "parameter",
    "max_nrows": "parameter",
}
GREEDY_TRACK_COMMIT_VALIDITY_BOUNDS = {
    "nhits": (1.0, None),
    "nfirst": (0.0, None),
    "nloss": (0.0, None),
    "loss_fraction": (0.0, 1.0),
    "min_nhits": (1.0, None),
    "max_nloss": (0.0, None),
    "max_nrows": (1.0, None),
}

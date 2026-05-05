"""Tests for the heuristic funnel index enrichment fields.

Validates that equivalence class hashing, exponent signatures, and invariant
forms are correctly computed for known symbolic expressions.
"""

from __future__ import annotations

import pytest
import sympy as sp

from sciona.ghost.symbolic import serialize_expr

from sciona.atoms.physics.symbolic_publication_manifest import (
    _canonical_zero_form,
    _exponent_signature,
    _exponent_signature_hash,
    _invariant_forms,
)


# ---------------------------------------------------------------------------
# Equivalence class hashing
# ---------------------------------------------------------------------------


class TestCanonicalZeroForm:
    """Algebraically equivalent rearrangements must produce the same hash."""

    def test_fma_equivalences(self) -> None:
        F, m, a = sp.symbols("F m a")
        h1 = _canonical_zero_form(serialize_expr(sp.Eq(F, m * a)))
        h2 = _canonical_zero_form(serialize_expr(sp.Eq(a, F / m)))
        h3 = _canonical_zero_form(serialize_expr(sp.Eq(F - m * a, 0)))
        assert h1 == h2 == h3

    def test_dispersion_delay_equivalences(self) -> None:
        K, DM, f, t = sp.symbols("K DM f t")
        h1 = _canonical_zero_form(serialize_expr(sp.Eq(t, K * DM * f ** -2)))
        h2 = _canonical_zero_form(serialize_expr(sp.Eq(K, t * f**2 / DM)))
        h3 = _canonical_zero_form(serialize_expr(sp.Eq(t - K * DM / f**2, 0)))
        assert h1 == h2 == h3

    def test_different_equations_differ(self) -> None:
        x, y, z = sp.symbols("x y z")
        h_linear = _canonical_zero_form(serialize_expr(sp.Eq(y, x)))
        h_quadratic = _canonical_zero_form(serialize_expr(sp.Eq(y, x**2)))
        assert h_linear != h_quadratic

    def test_ideal_gas_equivalences(self) -> None:
        P, V, n, R, T = sp.symbols("P V n R T")
        h1 = _canonical_zero_form(serialize_expr(sp.Eq(P * V, n * R * T)))
        h2 = _canonical_zero_form(serialize_expr(sp.Eq(P, n * R * T / V)))
        h3 = _canonical_zero_form(serialize_expr(sp.Eq(T, P * V / (n * R))))
        assert h1 == h2 == h3


# ---------------------------------------------------------------------------
# Exponent signatures
# ---------------------------------------------------------------------------


class TestExponentSignature:
    """Power-law expressions should yield correct exponent dicts."""

    def test_dispersion_delay(self) -> None:
        K, DM, f, t = sp.symbols("K DM f t")
        srepr = serialize_expr(sp.Eq(t, K * DM * f ** -2))
        sig = _exponent_signature(
            srepr,
            constants={"K": 4148.808},
            variables={"t": "output", "K": "constant", "DM": "input", "f": "input"},
        )
        assert sig is not None
        assert sig["DM"] == "1"
        assert sig["f"] == "-2"
        assert "K" not in sig  # constant should be excluded
        assert "t" not in sig  # output (LHS) should be excluded

    def test_inverse_square_law(self) -> None:
        G, m1, m2, r, F = sp.symbols("G m1 m2 r F")
        srepr = serialize_expr(sp.Eq(F, G * m1 * m2 * r ** -2))
        sig = _exponent_signature(
            srepr,
            constants={"G": 6.674e-11},
            variables={
                "F": "output",
                "G": "constant",
                "m1": "input",
                "m2": "input",
                "r": "input",
            },
        )
        assert sig is not None
        assert sig["m1"] == "1"
        assert sig["m2"] == "1"
        assert sig["r"] == "-2"

    def test_non_monomial_returns_none(self) -> None:
        A, w, t, y = sp.symbols("A w t y")
        srepr = serialize_expr(sp.Eq(y, A * sp.sin(w * t)))
        sig = _exponent_signature(
            srepr,
            constants={},
            variables={"y": "output", "A": "input", "w": "input", "t": "input"},
        )
        assert sig is None

    def test_hash_deterministic(self) -> None:
        K, DM, f, t = sp.symbols("K DM f t")
        srepr = serialize_expr(sp.Eq(t, K * DM * f ** -2))
        sig = _exponent_signature(
            srepr,
            constants={"K": 4148.808},
            variables={"t": "output", "K": "constant", "DM": "input", "f": "input"},
        )
        h1 = _exponent_signature_hash(sig)
        h2 = _exponent_signature_hash(sig)
        assert h1 is not None
        assert h1 == h2

    def test_none_signature_hashes_to_none(self) -> None:
        assert _exponent_signature_hash(None) is None


# ---------------------------------------------------------------------------
# Invariant forms
# ---------------------------------------------------------------------------


class TestInvariantForms:
    def test_dispersion_delay_isolates_K(self) -> None:
        K, DM, f, t = sp.symbols("K DM f t")
        srepr = serialize_expr(sp.Eq(t, K * DM * f ** -2))
        forms = _invariant_forms(
            srepr,
            variables={"t": "output", "K": "constant", "DM": "input", "f": "input"},
            constants={"K": 4148.808},
        )
        assert forms is not None
        assert len(forms) == 1
        form = forms[0]
        assert form["isolated_symbol"] == "K"
        assert form["known_value"] == 4148.808
        # The invariant expression should be t*f^2/DM
        assert "DM" in form["invariant_expr_text"]
        assert "f" in form["invariant_expr_text"] or "fchan" in form["invariant_expr_text"]

    def test_no_constants_returns_none(self) -> None:
        V, I, R = sp.symbols("V I R")
        srepr = serialize_expr(sp.Eq(V, I * R))
        forms = _invariant_forms(
            srepr,
            variables={"V": "output", "I": "input", "R": "input"},
            constants={},
        )
        assert forms is None

    def test_invariant_evaluates_to_constant(self) -> None:
        """The invariant expression should evaluate to the constant value."""
        import numpy as np

        K_val = 4148.808
        K, DM, f, t = sp.symbols("K DM f t")
        srepr = serialize_expr(sp.Eq(t, K * DM * f ** -2))
        forms = _invariant_forms(
            srepr,
            variables={"t": "output", "K": "constant", "DM": "input", "f": "input"},
            constants={"K": K_val},
        )
        assert forms is not None
        form = forms[0]

        # Compile the invariant expression and evaluate with synthetic data.
        from sciona.ghost.symbolic import deserialize_expr

        inv_expr = deserialize_expr(form["invariant_expr_srepr"])
        fn = sp.lambdify(sorted(inv_expr.free_symbols, key=str), inv_expr, "numpy")

        rng = np.random.default_rng(42)
        DM_data = rng.uniform(1, 100, 500)
        f_data = rng.uniform(100, 2000, 500)
        t_data = K_val * DM_data / f_data**2

        # Evaluate: the result should be K_val for every row.
        result = fn(DM_data, f_data, t_data)
        np.testing.assert_allclose(result, K_val, rtol=1e-10)

import importlib


def test_astroflow_import_smoke() -> None:
    assert importlib.import_module("sciona.atoms.physics.astroflow") is not None
    assert importlib.import_module("sciona.probes.physics.astroflow") is not None

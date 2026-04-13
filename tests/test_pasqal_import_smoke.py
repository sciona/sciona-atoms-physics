import importlib


def test_pasqal_import_smoke() -> None:
    assert importlib.import_module("sciona.atoms.physics.pasqal") is not None
    assert importlib.import_module("sciona.atoms.physics.pasqal.docking") is not None
    assert importlib.import_module("sciona.probes.physics.pasqal") is not None

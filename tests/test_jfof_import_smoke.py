import importlib


def test_jfof_import_smoke() -> None:
    assert importlib.import_module("sciona.atoms.physics.jFOF") is not None
    assert importlib.import_module("sciona.atoms.physics.jFOF.topo") is not None
    assert importlib.import_module("sciona.probes.physics.jFOF") is not None

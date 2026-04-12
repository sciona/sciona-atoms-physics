import importlib


def test_skyfield_import_smoke() -> None:
    assert importlib.import_module("sciona.atoms.physics.skyfield") is not None
    assert importlib.import_module("sciona.probes.physics.skyfield") is not None

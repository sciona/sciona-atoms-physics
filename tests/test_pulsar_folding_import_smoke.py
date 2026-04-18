import importlib


def test_pulsar_folding_import_smoke() -> None:
    assert importlib.import_module("sciona.atoms.physics.pulsar_folding") is not None
    assert importlib.import_module("sciona.atoms.physics.pulsar_folding.dm_can") is not None
    assert importlib.import_module("sciona.probes.physics.pulsar_folding") is not None

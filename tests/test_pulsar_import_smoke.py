import importlib


def test_pulsar_import_smoke() -> None:
    assert importlib.import_module("sciona.atoms.physics.pulsar") is not None
    assert importlib.import_module("sciona.atoms.physics.pulsar.pipeline") is not None
    assert importlib.import_module("sciona.probes.physics.pulsar") is not None

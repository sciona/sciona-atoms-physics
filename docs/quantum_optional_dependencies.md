# Pasqal Quantum Optional Dependencies

`sciona.atoms.physics.pasqal.docking.quantum_mwis_solver` uses the Pulser
neutral-atom sequence structure from the Molecular-Docking quantum solver source.

Install the optional quantum stack before running the Pulser-backed atom:

```bash
/Users/conrad/personal/sciona-matcher/.venv/bin/python -m pip install -e '.[quantum]'
```

The optional group pins the stack validated for this lane:

- `pulser==1.7.2`
- `pulser-simulation==1.7.2`
- `emu-sv==2.7.2`
- `emu-mps==2.7.2`
- `qutip==5.2.3`

Without these packages, normal Pasqal imports still work, but the quantum MWIS
solver raises `MissingQuantumOptionalDependency`. The optional backend tests
skip cleanly in base environments and run against real Pulser objects when the
extra is installed.

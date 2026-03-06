# Quickstart

This example builds and exports a basic framework.

```python
from veloxchem.molecule import Molecule
from mofbuilder import MetalOrganicFrameworkBuilder

linker = Molecule.read_smiles("O=C([O-])c1ccc(cc1)C(=O)[O-]")

builder = MetalOrganicFrameworkBuilder(mof_family="HKUST-1")
builder.node_metal = "Cu"
builder.linker_molecule = linker
builder.supercell = (1, 1, 1)

framework = builder.build()
framework.write(format=["cif", "xyz"], filename="output/hkust1")
```

See `docs/examples.md` for additional workflows including solvation and MD prep.

# Examples

## Example 1: Build and export

```python
from veloxchem.molecule import Molecule
from mofbuilder import MetalOrganicFrameworkBuilder

mof = MetalOrganicFrameworkBuilder(mof_family="UiO-66")
mof.node_metal = "Zr"
mof.linker_molecule = Molecule.read_smiles("O=C([O-])c1ccc(cc1)C(=O)[O-]")
framework = mof.build()
framework.write(format=["cif", "gro"], filename="output/uio66")
```

## Example 2: Solvation and MD input preparation

```python
from pathlib import Path

framework.target_directory = "output"
framework.solvate(
    solvents_files=[str(Path("database/solvents_database/TIP3P.xyz"))],
    solvents_proportions=[1.0],
    solvents_quantities=[500],
    padding_angstrom=12,
)
framework.md_prepare()
framework.md_driver.run_pipeline(steps=["em", "nvt"], nvt_time=20)
```

## Example 3: CLI metadata checks

```bash
mofbuilder --version
mofbuilder list-families
mofbuilder list-metals --mof-family HKUST-1
```

## Example 4: Defective MOF-5 workflow

Based on `examples/fig2_defective.ipynb`, this pattern builds MOF-5 variants
and applies replacement/removal edits.

```python
from mofbuilder import MetalOrganicFrameworkBuilder as MofBuilder
import veloxchem as vlx

bdc = vlx.Molecule.read_smiles("O=C([O-])C(C=C1)=CC=C1C([O-])=O")

mof = MofBuilder(mof_family="MOF-5")
mof.ostream.mute()
mof.linker_molecule = bdc
mof.node_metal = "Zn"
mof.termination = False
mof.supercell = (2, 2, 2)
nocap = mof.build()

new_linker = vlx.Molecule.read_smiles("O=C([O-])C(C=C1N)=C(N)C=C1C([O-])=O")
rp_variant = nocap.replace(replace_indices=[824, 816, 334], new_linker_molecule=new_linker)
rm_variant = nocap.remove(remove_indices=[50, 370, 63, 368])
```

# Installation

MOFBuilder depends on several scientific packages distributed via conda,
including VeloxChem, RDKit, OpenMM, and xtb-python.

## 1. Create environment

```bash
conda create -n mofbuilder python=3.10
conda activate mofbuilder
```

## 2. Install core scientific dependencies

```bash
conda install -c veloxchem -c conda-forge veloxchem ipykernel rdkit openmm xtb-python py3dmol
```

## 3. Optional: ML potentials for OpenMM

```bash
conda install -c conda-forge openmm-ml
```

## 4. Install MOFBuilder from source

```bash
git clone https://github.com/chenxili01/MofBuilder.git
cd MofBuilder
pip install -e .
```

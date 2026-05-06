"""VeloxChem compatibility boundary for MOFBuilder."""

from __future__ import annotations

import veloxchem as vlx

from veloxchem.environment import get_data_path
from veloxchem.errorhandler import assert_msg_critical
from veloxchem.mmforcefieldgenerator import MMForceFieldGenerator
from veloxchem.molecularbasis import MolecularBasis
from veloxchem.molecule import Molecule
from veloxchem.optimizationdriver import OptimizationDriver
from veloxchem.outputstream import OutputStream
from veloxchem.scfrestdriver import ScfRestrictedDriver
from veloxchem.scfunrestdriver import ScfUnrestrictedDriver
from veloxchem.veloxchemlib import (
    hartree_in_kcalpermol,
    hartree_in_kjpermol,
    mpi_master,
)
from veloxchem.xtbdriver import XtbDriver

__all__ = [
    "MMForceFieldGenerator",
    "MolecularBasis",
    "Molecule",
    "OptimizationDriver",
    "OutputStream",
    "ScfRestrictedDriver",
    "ScfUnrestrictedDriver",
    "XtbDriver",
    "assert_msg_critical",
    "get_data_path",
    "hartree_in_kcalpermol",
    "hartree_in_kjpermol",
    "mpi_master",
    "vlx",
]

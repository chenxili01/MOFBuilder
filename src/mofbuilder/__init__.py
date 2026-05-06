"""
MofBuilder: A Python library for building and analyzing Metal-Organic Frameworks (MOFs)

Copyright (C) 2024 MofBuilder Contributors

SPDX-License-Identifier: BSD-3-Clause
"""

from __future__ import annotations

from . import analysis, core, io, md, utils, visualization
from .core.builder import MetalOrganicFrameworkBuilder

__version__ = "0.1.0"
__author__ = "MofBuilder Contributors"
__email__ = "chenxili@kth.se"
__license__ = "BSD-3-Clause"

__all__ = [
    "MetalOrganicFrameworkBuilder",
    "analysis",
    "core",
    "io",
    "md",
    "utils",
    "visualization",
    "__version__",
]

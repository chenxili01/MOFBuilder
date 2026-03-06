API Reference
=============

This reference is intentionally conservative for CI stability and only lists
the documented public interface used in stable workflows.

Builder
-------

- ``mofbuilder.MetalOrganicFrameworkBuilder``
- ``mofbuilder.core.Framework``

Modelling and Simulation
------------------------

- ``mofbuilder.md.OpenmmSetup``
- ``mofbuilder.md.SolvationBuilder``
- ``mofbuilder.md.LinkerForceFieldGenerator``
- ``mofbuilder.md.GromacsForcefieldMerger``
- ``mofbuilder.md.ForceFieldMapper``

Input and Output
----------------

- ``mofbuilder.io.CifReader`` / ``mofbuilder.io.CifWriter``
- ``mofbuilder.io.PdbReader`` / ``mofbuilder.io.PdbWriter``
- ``mofbuilder.io.GroReader`` / ``mofbuilder.io.GroWriter``
- ``mofbuilder.io.XyzReader`` / ``mofbuilder.io.XyzWriter``

Visualization
-------------

- ``mofbuilder.visualization.Viewer``

Note
----

The analysis module is currently under development and is not yet part of the
public interface.

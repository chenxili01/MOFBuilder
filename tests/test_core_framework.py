from pathlib import Path
from types import SimpleNamespace

import numpy as np
import networkx as nx
import pytest

from mofbuilder.core.framework import Framework


class _FakeMofWriter:

    def __init__(self):
        self.calls = []
        self.residues_info = {"MOF": 1}
        self.edges_data = [np.array([["C", "C1", 1, "MOL", 1, 0, 0, 0, 1, 0, "C"]],
                                    dtype=object)]
        self.filename = None

    def only_get_merged_data(self):
        data = np.array([["C", "C1", 1, "MOL", 1, 0.0, 0.0, 0.0, 1.0, 0.0, "C"]],
                        dtype=object)
        return data, data.copy()

    def write_xyz(self, skip_merge=True):
        self.calls.append(("xyz", skip_merge))

    def write_cif(self, skip_merge=True, supercell_boundary=None, frame_cell_info=None):
        self.calls.append(("cif", skip_merge, tuple(supercell_boundary),
                           tuple(frame_cell_info)))

    def write_pdb(self, skip_merge=True):
        self.calls.append(("pdb", skip_merge))

    def write_gro(self, skip_merge=True):
        self.calls.append(("gro", skip_merge))


class _FakeSolvationBuilder:

    def __init__(self):
        self.solvents_files = []
        self.solute_data = None
        self.preferred_region_box = None
        self.solvents_proportions = []
        self.solvents_quantities = []
        self.target_directory = None
        self.box_size = None
        self.output_calls = []

    def solvate(self):
        return {"TIP3P": {"accepted_quantity": 5}}

    def _update_datalines(self):
        solv = np.array([["O", "O1", 1, "TIP3P", 2, 5.0, 5.0, 5.0, 1.0, 0.0, "O"]],
                        dtype=object)
        return self.solute_data, solv

    def write_output(self, output_file="solvated_structure", format=None):
        self.output_calls.append((output_file, tuple(format or [])))


@pytest.mark.core
def test_framework_get_merged_data_sets_arrays():
    fw = Framework()
    fw.mofwriter = _FakeMofWriter()
    fw.graph = object()
    fw.supercell_info = [10.0, 10.0, 10.0]
    fw.sc_unit_cell = np.eye(3)
    fw.xoo_dict = {}
    fw.dummy_atom_node_dict = {}
    fw.target_directory = "tests/output"
    fw.supercell = [1, 1, 1]

    fw.get_merged_data()

    assert fw.framework_data is not None
    assert fw.framework_fcoords_data is not None
    assert fw.residues_info == {"MOF": 1}


@pytest.mark.core
def test_framework_get_merged_data_forwards_role_aware_metadata_to_writer():
    role_dummy_atom_node_dict = {
        "node:alpha": {
            "dummy_atom_node_dict": {
                "METAL_count": 1,
                "dummy_res_len": 1,
                "HHO_count": 0,
                "HO_count": 1,
                "O_count": 0,
            }
        }
    }
    role_xoo_dict = {
        "node:alpha": {
            "xoo_dict": {
                1: [2, 3],
            }
        }
    }
    graph = {"graph": "role-aware"}

    class ForwardingWriter(_FakeMofWriter):

        def only_get_merged_data(self):
            assert self.G is graph
            assert self.xoo_dict == role_xoo_dict
            assert self.dummy_atom_node_dict == role_dummy_atom_node_dict
            return super().only_get_merged_data()

    fw = Framework()
    fw.mofwriter = ForwardingWriter()
    fw.graph = graph
    fw.supercell_info = [10.0, 10.0, 10.0]
    fw.sc_unit_cell = np.eye(3)
    fw.xoo_dict = role_xoo_dict
    fw.dummy_atom_node_dict = role_dummy_atom_node_dict
    fw.target_directory = "tests/output"
    fw.supercell = [1, 1, 1]

    fw.get_merged_data()

    assert fw.framework_data is not None
    assert fw.framework_fcoords_data is not None


@pytest.mark.core
def test_framework_write_dispatches_formats(tmp_path):
    fw = Framework()
    fake_writer = _FakeMofWriter()
    fw.mofwriter = fake_writer
    fw.mof_family = "MOF-TEST"
    fw.supercell = [1, 1, 1]
    fw.supercell_info = [10.0, 10.0, 10.0]
    fw.framework_data = np.array([["C", "C1", 1, "MOL", 1, 0, 0, 0, 1, 0, "C"]],
                                 dtype=object)
    fw.framework_fcoords_data = fw.framework_data.copy()
    fw.graph = type("G", (), {"nodes": {}})()

    out = tmp_path / "stage3_framework_output"
    fw.write(format=["xyz", "cif", "pdb", "gro"], filename=str(out))

    call_names = [c[0] for c in fake_writer.calls]
    assert call_names == ["xyz", "cif", "pdb", "gro"]
    assert fw.filename.endswith("stage3_framework_output")


@pytest.mark.core
def test_framework_solvate_and_md_prepare(monkeypatch, tmp_path):
    fw = Framework()
    fw.mof_family = "MOF-TEST"
    fw.target_directory = str(tmp_path)
    fw.data_path = str(Path(__file__).resolve().parent / "database")
    fw.supercell_info = np.array([20.0, 20.0, 20.0, 90.0, 90.0, 90.0])
    fw.framework_data = np.array([["C", "C1", 1, "MOF", 1, 0.0, 0.0, 0.0, 1.0, 0.0, "C"]],
                                 dtype=object)
    fw.residues_info = {"MOF": 1}
    fw.node_metal = "Zr"
    fw.dummy_atom_node = False
    fw.termination_name = "acetate"
    fw.solvents = ["TIP3P.xyz"]
    fw.mofwriter = _FakeMofWriter()

    fake_solv = _FakeSolvationBuilder()
    fw.solvationbuilder = fake_solv

    fw.solvate(solvents_files=["TIP3P.xyz"],
               solvents_proportions=[1],
               solvents_quantities=[5])

    assert fw.solvents_dict == {"TIP3P": {"accepted_quantity": 5}}
    assert fw.solvated_gro_file.endswith("MOF-TEST_in_solvent.gro")
    assert fw.solvation_system_data.shape[0] == 2

    # Stage md_prepare with patched heavy collaborators.
    import mofbuilder.core.framework as fw_mod

    class FakeGromacsForcefieldMerger:

        def __init__(self):
            self.top_path = str(tmp_path / "system.top")

        def generate_MOF_gromacsfile(self):
            return None

    class FakeOpenmmSetup:

        def __init__(self, gro_file, top_file, comm=None, ostream=None):
            self.gro_file = gro_file
            self.top_file = top_file
            self.system_pbc = True

    monkeypatch.setattr(fw_mod, "GromacsForcefieldMerger",
                        FakeGromacsForcefieldMerger)
    monkeypatch.setattr(fw_mod, "OpenmmSetup", FakeOpenmmSetup)

    def fake_generate_linker_forcefield(self):
        self.linker_ff_gen = SimpleNamespace(linker_ff_name="Linker")

    monkeypatch.setattr(Framework, "generate_linker_forcefield",
                        fake_generate_linker_forcefield)

    fw.md_prepare()

    assert fw.gmx_ff.top_path.endswith("system.top")
    assert fw.md_driver.gro_file.endswith("MOF-TEST_in_solvent.gro")


@pytest.mark.core
def test_framework_remove_and_replace_return_new_framework_instances(monkeypatch):
    remove_merge_calls = []
    replace_merge_calls = []

    class FakeDefectGenerator:

        def __init__(self, comm=None, ostream=None):
            self.updated_matched_vnode_xind = [("VA_0", 1, "EDGE_0")]
            self.updated_unsaturated_nodes = ["VA_0"]
            self.unsaturated_linkers = ["EDGE_0"]
            self.xoo_dict = None
            self.new_node_data = None
            self.new_node_X_data = None
            self.new_linker_data = None
            self.new_linker_X_data = None

        def remove_items_or_terminate(self, remove_indices, cleaved_eG):
            return cleaved_eG.copy()

        def replace_items(self, replace_indices, G):
            return G.copy()

    def fake_remove_merge(self, extra_graph=None):
        remove_merge_calls.append(self.graph if extra_graph is None else extra_graph)
        self.framework_data = np.array([["R"]], dtype=object)
        self.framework_fcoords_data = self.framework_data.copy()

    def fake_replace_merge(self, extra_graph=None):
        replace_merge_calls.append(self.graph if extra_graph is None else extra_graph)
        self.framework_data = np.array([["P"]], dtype=object)
        self.framework_fcoords_data = self.framework_data.copy()

    import mofbuilder.core.framework as fw_mod

    monkeypatch.setattr(fw_mod, "TerminationDefectGenerator", FakeDefectGenerator)

    remove_fw = Framework()
    remove_fw.graph = nx.Graph()
    remove_fw.graph.add_node("VA_0")
    remove_fw.termination = False
    remove_fw.linker_connectivity = 2
    remove_fw.node_connectivity = 4
    remove_fw.add_virtual_edge = False
    remove_fw.graph_index_name_dict = {1: "VA_0"}
    remove_fw.sc_unit_cell = np.eye(3)
    remove_fw.sc_unit_cell_inv = np.eye(3)
    remove_fw.clean_unsaturated_linkers = False
    remove_fw.update_node_termination = True
    remove_fw.matched_vnode_xind = []
    remove_fw.xoo_dict = {"node:alpha": {"xoo_dict": {1: [2, 3]}}}
    remove_fw.unsaturated_linkers = []
    remove_fw.unsaturated_nodes = []
    monkeypatch.setattr(Framework, "get_merged_data", fake_remove_merge)

    removed = remove_fw.remove(remove_indices=[1])

    assert removed is not remove_fw
    assert isinstance(removed, Framework)
    assert remove_merge_calls == [removed.graph]

    replace_fw = Framework()
    replace_fw.graph = nx.Graph()
    replace_fw.graph.add_node("VA_0")
    replace_fw.termination = False
    replace_fw.linker_connectivity = 2
    replace_fw.node_connectivity = 4
    replace_fw.add_virtual_edge = False
    replace_fw.graph_index_name_dict = {1: "VA_0"}
    replace_fw.sc_unit_cell = np.eye(3)
    replace_fw.sc_unit_cell_inv = np.eye(3)
    replace_fw.clean_unsaturated_linkers = False
    replace_fw.update_node_termination = True
    replace_fw.unsaturated_linkers = []
    replace_fw.unsaturated_nodes = []
    monkeypatch.setattr(Framework, "get_merged_data", fake_replace_merge)

    replaced = replace_fw.replace(replace_indices=[1])

    assert replaced is not replace_fw
    assert isinstance(replaced, Framework)
    assert replace_merge_calls == [replaced.graph]

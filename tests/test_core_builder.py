from types import MethodType, SimpleNamespace

import networkx as nx
import numpy as np
import pytest

import mofbuilder.core.builder as builder_module
from mofbuilder.core.builder import MetalOrganicFrameworkBuilder


class _DummyDefectGenerator:

    def __init__(self):
        self.updated_matched_vnode_xind = []
        self.updated_unsaturated_nodes = []
        self.unsaturated_linkers = []
        self.unsaturated_nodes = []

    def remove_items_or_terminate(self, res_idx2rm, cleaved_eG):
        self.updated_matched_vnode_xind = [("V0", 0, "E0")]
        self.updated_unsaturated_nodes = ["V_unsat"]
        self.unsaturated_linkers = ["L_unsat"]
        return cleaved_eG


class _ComparableTable:

    def __init__(self, rows):
        self._data = np.array(rows, dtype=object)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __eq__(self, other):
        if isinstance(other, _ComparableTable):
            return np.array_equal(self._data, other._data)
        return False

    def __repr__(self):
        return repr(self._data)


@pytest.mark.core
def test_builder_build_orchestrates_and_returns_framework(monkeypatch):
    builder = MetalOrganicFrameworkBuilder(mof_family="MOF-TEST")
    builder.defectgenerator = _DummyDefectGenerator()

    call_order = []

    def fake_load(self):
        call_order.append("load")
        self.data_path = "tests/database"
        self.target_directory = "tests/output"
        self.mof_family = "MOF-TEST"
        self.node_metal = "Zr"
        self.dummy_atom_node = False
        self.net_spacegroup = "P1"
        self.net_cell_info = [10.0, 10.0, 10.0, 90.0, 90.0, 90.0]
        self.net_unit_cell = np.eye(3)
        self.node_connectivity = 6
        self.linker_connectivity = 2
        self.linker_frag_length = 1.54
        self.node_data = np.array([["Zr", "Zr", 1, "MOL", 1, 0, 0, 0, 1, 0, "Zr"]],
                                  dtype=object)
        self.dummy_atom_node_dict = {"METAL_count": 1}
        self.termination = True
        self.termination_name = "acetate"
        self.termination_data = np.array([["X", "C", 1, "TER", 1, 0, 0, 0, 1, 0, "X"]],
                                         dtype=object)
        self.termination_X_data = self.termination_data.copy()
        self.termination_Y_data = self.termination_data.copy()
        self.frame_linker.molecule = object()

    def fake_optimize(self):
        call_order.append("optimize")
        self.frame_cell_info = [20.0, 20.0, 20.0, 90.0, 90.0, 90.0]
        self.frame_unit_cell = np.eye(3) * 20.0
        self.net_optimizer = SimpleNamespace(
            sc_unit_cell=np.eye(3) * 20.0,
            sc_unit_cell_inv=np.linalg.inv(np.eye(3) * 20.0),
        )

    def fake_supercell(self):
        call_order.append("supercell")
        g = nx.Graph()
        g.add_node("V0", index=0, fcoords=np.array([[0.1, 0.1, 0.1]]))
        g.add_node("E0", index=1, fcoords=np.array([[0.3, 0.3, 0.3]]))
        g.add_edge("V0", "E0")
        self.eG = g.copy()
        self.cleaved_eG = g.copy()
        self.eG_index_name_dict = {0: "V0", 1: "E0"}
        self.eG_matched_vnode_xind = [("V0", 0, "E0")]
        self.supercell_info = [20.0, 20.0, 20.0]
        self.edgegraphbuilder = SimpleNamespace(
            eG_index_name_dict=self.eG_index_name_dict,
            matched_vnode_xind=self.eG_matched_vnode_xind,
            unsaturated_linkers=[],
            unsaturated_nodes=[],
            xoo_dict={},
        )

    monkeypatch.setattr(MetalOrganicFrameworkBuilder, "load_framework", fake_load)
    monkeypatch.setattr(MetalOrganicFrameworkBuilder, "optimize_framework",
                        fake_optimize)
    monkeypatch.setattr(MetalOrganicFrameworkBuilder, "make_supercell",
                        fake_supercell)

    def fake_get_merged_data(self):
        self.framework_data = np.array(
            [["C", "C1", 1, "MOL", 1, 0.0, 0.0, 0.0, 1.0, 0.0, "C"]],
            dtype=object,
        )
        self.framework_fcoords_data = self.framework_data.copy()
        self.residues_info = {"MOL": 1}

    builder.framework.get_merged_data = MethodType(fake_get_merged_data,
                                                   builder.framework)

    framework = builder.build()

    assert call_order == ["load", "optimize", "supercell"]
    assert framework is builder.framework
    assert framework.mof_family == "MOF-TEST"
    assert framework.node_metal == "Zr"
    assert framework.graph.number_of_nodes() == 2
    assert framework.graph.number_of_edges() == 1
    assert framework.framework_data is not None


@pytest.mark.core
def test_initialize_role_registries_normalizes_scalar_inputs_to_default_roles():
    builder = MetalOrganicFrameworkBuilder(mof_family="MOF-TEST")
    builder.node_connectivity = 6
    builder.linker_connectivity = 2
    builder.node_metal = "Zr"
    builder.dummy_atom_node = False
    builder.linker_smiles = "C1=CC=CC=C1"
    builder.linker_charge = -2
    builder.linker_multiplicity = 1
    builder.mof_top_library.role_metadata = None

    builder._initialize_role_registries()

    assert builder.role_metadata is None
    assert builder.node_role_specs == {
        "node:default": {
            "role_id": "node:default",
            "expected_connectivity": 6,
            "topology_labels": [],
        }
    }
    assert builder.edge_role_specs == {
        "edge:default": {
            "role_id": "edge:default",
            "linker_connectivity": 2,
            "topology_labels": [],
        }
    }
    assert builder.node_role_registry["node:default"]["fragment_source"] == {
        "kind": "database",
        "keywords": ["6c", "Zr"],
        "exclude_keywords": ["dummy"],
    }
    assert builder.edge_role_registry["edge:default"]["fragment_source"] == {
        "kind": "smiles",
        "value": "C1=CC=CC=C1",
    }
    assert builder.edge_role_registry["edge:default"]["linker_charge"] == -2
    assert builder.edge_role_registry["edge:default"]["linker_multiplicity"] == 1


@pytest.mark.core
def test_role_registries_consume_phase_two_metadata_without_local_role_maps():
    builder = MetalOrganicFrameworkBuilder(mof_family="MOF-MULTI")
    builder.node_connectivity = 8
    builder.linker_connectivity = 4
    builder.node_metal = "Zn"
    builder.dummy_atom_node = True
    builder.linker_xyzfile = "tests/database/example_linker.xyz"
    builder.mof_top_library.role_metadata = {
        "schema": "mof_topology_role_metadata/v1",
        "node_roles": [
            {
                "role_id": "node:cluster",
                "expected_connectivity": 8,
                "topology_labels": ["V_A"],
            },
            {
                "role_id": "node:porphyrin",
                "expected_connectivity": 4,
                "topology_labels": ["V_B"],
            },
        ],
        "edge_roles": [
            {
                "role_id": "edge:tetratopic",
                "linker_connectivity": 4,
                "topology_labels": ["EC_B"],
            },
            {
                "role_id": "edge:ditopic",
                "linker_connectivity": 2,
                "topology_labels": ["EC_A"],
            },
        ],
    }

    builder._initialize_role_registries()

    assert list(builder.node_role_specs) == ["node:cluster", "node:porphyrin"]
    assert list(builder.edge_role_specs) == ["edge:tetratopic", "edge:ditopic"]
    assert builder.node_role_registry["node:porphyrin"]["fragment_source"] == {
        "kind": "database",
        "keywords": ["4c", "Zn"],
        "exclude_keywords": ["dummy"],
    }
    assert builder.edge_role_registry["edge:ditopic"]["fragment_source"] == {
        "kind": "xyzfile",
        "value": "tests/database/example_linker.xyz",
    }

    builder.frame_nodes.filename = "tests/database/node_8c_Zn.pdb"
    builder.node_data = np.array([["Zn"]], dtype=object)
    builder.node_X_data = np.array([["X"]], dtype=object)
    builder.dummy_atom_node_dict = {"Zn": 1}
    builder.linker_center_data = np.array([["C"]], dtype=object)
    builder.linker_center_X_data = np.array([["X"]], dtype=object)
    builder.linker_outer_data = np.array([["O"]], dtype=object)
    builder.linker_outer_X_data = np.array([["XO"]], dtype=object)
    builder.linker_frag_length = 12.5
    builder.linker_fake_edge = False

    builder._update_node_role_registry_data()
    builder._update_edge_role_registry_data()

    assert builder.node_role_registry["node:cluster"]["node_data"] is builder.node_data
    assert builder.node_role_registry["node:cluster"]["filename"] == (
        "tests/database/node_8c_Zn.pdb"
    )
    assert builder.node_role_registry["node:porphyrin"]["node_data"] is None
    assert (
        builder.edge_role_registry["edge:tetratopic"]["linker_frag_length"] == 12.5
    )
    assert builder.edge_role_registry["edge:tetratopic"]["linker_center_data"] is (
        builder.linker_center_data
    )
    assert builder.edge_role_registry["edge:ditopic"]["linker_center_data"] is None


@pytest.mark.core
def test_load_framework_single_role_keeps_scalar_state_and_populates_default_role_registries(
    monkeypatch,
):
    builder = MetalOrganicFrameworkBuilder(mof_family="MOF-TEST")
    builder.data_path = "tests/database"
    builder.node_metal = "Zr"
    builder.dummy_atom_node = False
    builder.linker_smiles = "C1=CC=CC=C1"
    builder.linker_charge = -2
    builder.linker_multiplicity = 1
    builder.termination = False

    initial_scalar_state = {
        "node_metal": builder.node_metal,
        "dummy_atom_node": builder.dummy_atom_node,
        "linker_smiles": builder.linker_smiles,
        "linker_charge": builder.linker_charge,
        "linker_multiplicity": builder.linker_multiplicity,
        "termination": builder.termination,
    }

    net_graph = nx.Graph()
    net_graph.add_node("V0", node_role_id="node:default")
    net_graph.add_node("V1", node_role_id="node:default")
    net_graph.add_edge("V0", "V1", edge_role_id="edge:default")

    def fake_fetch(mof_family):
        assert mof_family == "MOF-TEST"
        builder.mof_top_library.node_connectivity = 6
        builder.mof_top_library.role_metadata = None
        return "tests/database/template_database/MOF-TEST.cif"

    def fake_create_net():
        builder.frame_net.max_degree = 6
        builder.frame_net.cifreader.spacegroup = "P1"
        builder.frame_net.cell_info = [10.0, 10.0, 10.0, 90.0, 90.0, 90.0]
        builder.frame_net.unit_cell = np.eye(3)
        builder.frame_net.unit_cell_inv = np.eye(3)
        builder.frame_net.linker_connectivity = 2
        builder.frame_net.sorted_nodes = ["V0", "V1"]
        builder.frame_net.sorted_edges = [("V0", "V1")]
        builder.frame_net.pair_vertex_edge = [("V0", "V1", "E0")]
        builder.frame_net.G = net_graph.copy()

    linker_center_data = _ComparableTable(
        [
            ["C", "C1", 1, "LIG", 1, "0.0", "0.0", "0.0", 1.0, 0.0, "C"],
            ["C", "C2", 1, "LIG", 1, "1.5", "0.0", "0.0", 1.0, 0.0, "C"],
        ]
    )
    linker_center_x_data = _ComparableTable(
        [
            ["X", "X1", 1, "LIG", 1, "0.0", "0.0", "0.0", 1.0, 0.0, "X"],
            ["X", "X2", 1, "LIG", 1, "1.5", "0.0", "0.0", 1.0, 0.0, "X"],
        ]
    )

    def fake_linker_create(molecule=None):
        assert molecule is not None
        builder.frame_linker.linker_center_data = linker_center_data
        builder.frame_linker.linker_center_X_data = linker_center_x_data
        builder.frame_linker.linker_outer_data = None
        builder.frame_linker.linker_outer_X_data = None
        builder.frame_linker.fake_edge = False

    node_data = (("Zr", "Zr1"),)
    node_x_data = (("X", "X1"),)
    dummy_atom_node_dict = {"METAL_count": 1}

    def fake_node_create():
        builder.frame_nodes.node_data = node_data
        builder.frame_nodes.node_X_data = node_x_data
        builder.frame_nodes.dummy_node_split_dict = dummy_atom_node_dict

    monkeypatch.setattr(builder.mof_top_library, "fetch", fake_fetch)
    monkeypatch.setattr(builder.frame_net, "create_net", fake_create_net)
    monkeypatch.setattr(builder.frame_linker, "create", fake_linker_create)
    monkeypatch.setattr(builder.frame_nodes, "create", fake_node_create)
    monkeypatch.setattr(
        builder_module,
        "fetch_pdbfile",
        lambda *_args, **_kwargs: ["node_6c_Zr.pdb"],
    )

    builder.load_framework()

    assert builder.node_metal == initial_scalar_state["node_metal"]
    assert builder.dummy_atom_node == initial_scalar_state["dummy_atom_node"]
    assert builder.linker_smiles == initial_scalar_state["linker_smiles"]
    assert builder.linker_charge == initial_scalar_state["linker_charge"]
    assert builder.linker_multiplicity == initial_scalar_state["linker_multiplicity"]
    assert builder.termination == initial_scalar_state["termination"]
    assert builder.node_connectivity == 6
    assert builder.linker_connectivity == 2
    assert builder.linker_center_data == linker_center_data
    assert builder.linker_center_X_data == linker_center_x_data
    assert builder.linker_frag_length == 1.5
    assert builder.node_data == node_data
    assert builder.node_X_data == node_x_data
    assert builder.dummy_atom_node_dict == dummy_atom_node_dict

    assert builder.node_role_registry == {
        "node:default": {
            "role_id": "node:default",
            "expected_connectivity": 6,
            "topology_labels": [],
            "node_metal": "Zr",
            "dummy_atom_node": False,
            "fragment_source": {
                "kind": "database",
                "keywords": ["6c", "Zr"],
                "exclude_keywords": ["dummy"],
            },
            "filename": "tests/database/nodes_database/node_6c_Zr.pdb",
            "node_data": node_data,
            "node_X_data": node_x_data,
            "dummy_atom_node_dict": dummy_atom_node_dict,
        }
    }
    assert builder.edge_role_registry == {
        "edge:default": {
            "role_id": "edge:default",
            "linker_connectivity": 2,
            "topology_labels": [],
            "fragment_source": {
                "kind": "smiles",
                "value": "C1=CC=CC=C1",
            },
            "linker_charge": -2,
            "linker_multiplicity": 1,
            "linker_center_data": linker_center_data,
            "linker_center_X_data": linker_center_x_data,
            "linker_outer_data": None,
            "linker_outer_X_data": None,
            "linker_frag_length": 1.5,
            "linker_fake_edge": False,
        }
    }

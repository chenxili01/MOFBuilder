import numpy as np
import networkx as nx

from mofbuilder.core.write import MofWriter


def test_remove_xoo_from_node_sets_noxoo_points():
    w = MofWriter()
    g = nx.Graph()
    node_points = np.array([
        ["C", "C", 0.0, 0.0, 0.0],
        ["X", "X", 0.1, 0.0, 0.0],
        ["O", "O", 0.2, 0.0, 0.0],
        ["O", "O", 0.3, 0.0, 0.0],
    ], dtype=object)
    g.add_node("V_0", f_points=node_points)
    g.add_node("EDGE_0", f_points=node_points)

    out = w._remove_xoo_from_node(g, {1: [2, 3]})

    assert out.nodes["V_0"]["noxoo_f_points"].shape[0] == 1
    assert "noxoo_f_points" not in out.nodes["EDGE_0"]


def test_rename_node_name_returns_ordered_data():
    w = MofWriter()

    # One node with 3 atoms: METAL(1), HO(2)
    node = np.array([
        ["Zr", "Zr", 1, "OLD", 1, 0.0, 0.0, 0.0, 0, 0.0, ""],
        ["O", "O", 2, "OLD", 1, 1.0, 0.0, 0.0, 0, 0.0, ""],
        ["H", "H", 3, "OLD", 1, 1.1, 0.0, 0.0, 0, 0.0, ""],
    ], dtype=object)

    renamed = w._rename_node_name(
        nodes_data=[node],
        dummy_atom_node_dict={
            "METAL_count": 1,
            "dummy_res_len": 1,
            "HHO_count": 0,
            "HO_count": 1,
            "O_count": 0,
        },
    )

    assert renamed.shape[1] == 11
    assert renamed[0, 3].startswith("METAL_")
    assert renamed[1, 3].startswith("HO_")


def test_get_merged_data_keeps_single_role_dummy_atom_behavior():
    w = MofWriter()
    node = np.array([
        ["Zr", "Zr", 1, "OLD", 1, 0.0, 0.0, 0.0, 0, 0.0, ""],
        ["O", "O", 2, "OLD", 1, 1.0, 0.0, 0.0, 0, 0.0, ""],
        ["H", "H", 3, "OLD", 1, 1.1, 0.0, 0.0, 0, 0.0, ""],
    ], dtype=object)
    g = nx.Graph()
    g.add_node("V_0", node_role_id="node:default")
    g.add_node("V_1", node_role_id="node:default")

    w.nodes_data = [node.copy(), node.copy()]
    w.node_names = ["V_0", "V_1"]
    w.edges_data = []
    w.terms_data = []
    w.cG = g

    merged = w.get_merged_data({
        "METAL_count": 1,
        "dummy_res_len": 1,
        "HHO_count": 0,
        "HO_count": 1,
        "O_count": 0,
    })

    assert list(merged[:, 3]) == [
        "METAL_1",
        "METAL_1",
        "HO_2",
        "HO_2",
        "HO_2",
        "HO_2",
    ]
    assert w.residues_info["METAL"] == 2
    assert w.residues_info["HO"] == 2
    assert w.residues_info[";NODE"] == 2


def test_writer_resolves_role_specific_dummy_and_xoo_metadata():
    w = MofWriter()
    g = nx.Graph()
    alpha_points = np.array([
        ["C", "C", 0.0, 0.0, 0.0],
        ["X", "X", 0.1, 0.0, 0.0],
        ["O", "O", 0.2, 0.0, 0.0],
        ["O", "O", 0.3, 0.0, 0.0],
    ], dtype=object)
    beta_points = np.array([
        ["X", "X", 0.0, 0.2, 0.0],
        ["O", "O", 0.0, 0.3, 0.0],
        ["O", "O", 0.0, 0.4, 0.0],
        ["H", "H", 0.0, 0.5, 0.0],
    ], dtype=object)
    g.add_node("VA_0", f_points=alpha_points, node_role_id="node:alpha")
    g.add_node("VB_0", f_points=beta_points, node_role_id="node:beta")

    trimmed = w._remove_xoo_from_node(g, {
        "node:alpha": {
            "xoo_dict": {
                1: [2, 3],
            }
        },
        "node:beta": {
            "xoo_dict": {
                0: [1, 2],
            }
        },
    })

    assert trimmed.nodes["VA_0"]["noxoo_f_points"][:, 0].tolist() == ["C"]
    assert trimmed.nodes["VB_0"]["noxoo_f_points"][:, 0].tolist() == ["H"]

    alpha_node = np.array([
        ["Zr", "Zr", 1, "OLD", 1, 0.0, 0.0, 0.0, 0, 0.0, ""],
        ["O", "O", 2, "OLD", 1, 1.0, 0.0, 0.0, 0, 0.0, ""],
        ["H", "H", 3, "OLD", 1, 1.1, 0.0, 0.0, 0, 0.0, ""],
    ], dtype=object)
    beta_node = np.array([
        ["O", "O", 1, "OLD", 2, 2.0, 0.0, 0.0, 0, 0.0, ""],
    ], dtype=object)

    w.nodes_data = [alpha_node, beta_node]
    w.node_names = ["VA_0", "VB_0"]
    w.edges_data = []
    w.terms_data = []
    w.cG = g

    merged = w.get_merged_data({
        "node:alpha": {
            "dummy_atom_node_dict": {
                "METAL_count": 1,
                "dummy_res_len": 1,
                "HHO_count": 0,
                "HO_count": 1,
                "O_count": 0,
            }
        },
        "node:beta": {
            "dummy_atom_node_dict": {
                "METAL_count": 0,
                "dummy_res_len": 1,
                "HHO_count": 0,
                "HO_count": 0,
                "O_count": 1,
            }
        },
    })

    assert list(merged[:, 3]) == ["METAL_1", "HO_2", "HO_2", "O_1"]
    assert w.residues_info["METAL"] == 1
    assert w.residues_info["HO"] == 1
    assert w.residues_info["O"] == 1

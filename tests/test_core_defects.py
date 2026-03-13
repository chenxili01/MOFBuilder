import networkx as nx
import numpy as np

from mofbuilder.core.defects import TerminationDefectGenerator


def _make_graph():
    g = nx.Graph()
    g.add_node("V_0", index=1)
    g.add_node("V_1", index=2)
    g.add_node("EDGE_0", index=-1)
    g.add_edge("V_0", "EDGE_0", type="real")
    g.add_edge("V_1", "EDGE_0", type="real")
    return g


def test_find_unsaturated_nodes_and_linkers():
    gen = TerminationDefectGenerator()
    g = _make_graph()

    unsat_nodes = gen._find_unsaturated_nodes(g, node_connectivity=2)
    unsat_linkers = gen._find_unsaturated_linkers(g, linker_topics=3)

    assert set(unsat_nodes) == {"V_0", "V_1"}
    assert unsat_linkers == ["EDGE_0"]


def test_extract_node_names_from_index_dict():
    gen = TerminationDefectGenerator()

    out = gen._extract_node_name_from_eG_dict([1, 3], {1: "V_0", 2: "EDGE_0"})

    assert out == ["V_0"]


def test_update_matched_nodes_xind_drops_removed_nodes_or_edges():
    gen = TerminationDefectGenerator()

    old = [("V_0", 1, "EDGE_0"), ("V_1", 2, "EDGE_1")]
    new = gen._update_matched_nodes_xind(["V_0", "EDGE_1"], old)

    assert new == []


def test_remove_xoo_from_node_keeps_single_role_xoo_dict():
    gen = TerminationDefectGenerator()
    gen.xoo_dict = {1: [2, 3]}
    g = nx.Graph()
    g.add_node("V_0",
               f_points=[
                   ["C", "C", 0.0, 0.0, 0.0],
                   ["X", "X", 0.1, 0.0, 0.0],
                   ["O", "O", 0.2, 0.0, 0.0],
                   ["O", "O", 0.3, 0.0, 0.0],
               ])

    out = gen._remove_xoo_from_node(g)

    assert out.nodes["V_0"]["noxoo_f_points"].shape == (1, 5)
    assert out.nodes["V_0"]["noxoo_f_points"][0, 0:2].tolist() == ["C", "C"]


def test_make_unsaturated_vnode_xoo_dict_uses_role_specific_xoo_metadata():
    gen = TerminationDefectGenerator()
    eG = nx.Graph()
    eG.add_node(
        "VA_0",
        index=1,
        node_role_id="node:alpha",
        f_points=np.array([
            ["C", "C", 0.0, 0.0, 0.0],
            ["X", "X", 0.1, 0.0, 0.0],
            ["O", "O", 0.2, 0.0, 0.0],
            ["O", "O", 0.3, 0.0, 0.0],
        ], dtype=object),
    )
    eG.add_node(
        "VB_0",
        index=2,
        node_role_id="node:beta",
        f_points=np.array([
            ["X", "X", 0.0, 0.1, 0.0],
            ["O", "O", 0.0, 0.2, 0.0],
            ["O", "O", 0.0, 0.3, 0.0],
            ["H", "H", 0.0, 0.4, 0.0],
        ], dtype=object),
    )

    unsat_xind, unsat_xoo, matched = gen._make_unsaturated_vnode_xoo_dict(
        unsaturated_nodes=["VA_0", "VB_0"],
        xoo_dict={
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
        },
        matched_vnode_xind=[],
        eG=eG,
        sc_unit_cell=np.eye(3),
    )

    assert unsat_xind == {"VA_0": [1], "VB_0": [0]}
    assert matched == {}
    assert unsat_xoo[("VA_0", 1)]["oo_ind"] == [2, 3]
    assert unsat_xoo[("VB_0", 0)]["oo_ind"] == [1, 2]

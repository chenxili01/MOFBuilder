import networkx as nx
import numpy as np
import pytest

from mofbuilder.core.linker import FrameLinker


class _ToyMolecule:

    def __init__(self):
        self._labels = ["C", "O", "O", "C", "O", "O", "H", "H"]
        self._coords = np.array(
            [
                [0.0, 0.0, 0.0],    # 0
                [1.2, 0.0, 0.0],    # 1
                [-1.2, 0.0, 0.0],   # 2
                [3.0, 0.0, 0.0],    # 3
                [4.2, 0.0, 0.0],    # 4
                [1.8, 0.0, 0.0],    # 5
                [5.4, 0.0, 0.0],    # 6
                [-2.4, 0.0, 0.0],   # 7
            ])
        self._matrix = np.array(
            [
                [0, 1, 1, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 1, 1, 0, 0],
                [0, 0, 0, 1, 0, 0, 1, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
            ],
            dtype=int,
        )

    def get_connectivity_matrix(self):
        return self._matrix

    def get_coordinates_in_angstrom(self):
        return self._coords.copy()

    def get_labels(self):
        return list(self._labels)

    def get_distance_matrix_in_angstrom(self):
        d = self._coords[:, None, :] - self._coords[None, :, :]
        return np.linalg.norm(d, axis=2)

    def center_of_mass_in_bohr(self):
        return np.mean(self._coords, axis=0) / 0.529177


@pytest.mark.core
def test_linker_boundary_helpers():
    g = nx.Graph()
    g.add_node(0, label="C")
    g.add_node(1, label="O")
    g.add_node(2, label="O")
    g.add_node(3, label="H")
    g.add_node(10, label="C")
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(2, 3)
    g.add_edge(0, 10)

    boundary = FrameLinker._find_boundary_atom(g, boundary_labels=["O"])
    assert (1, 0) in boundary

    center, dist = FrameLinker.find_closest_center_node(g, [10], 0)
    assert center == 10
    assert dist == 1


@pytest.mark.core
def test_linker_create_lg_excludes_metal_edges():
    linker = FrameLinker()
    toy = _ToyMolecule()
    linker._create_lG(toy)

    assert linker.lG.number_of_nodes() == len(toy.get_labels())
    assert linker.metals == []
    assert linker.lG.number_of_edges() > 0


@pytest.mark.core
def test_linker_process_molecule_and_create_for_ditopic():
    linker = FrameLinker()
    linker.linker_connectivity = 2
    linker.process_linker_molecule(_ToyMolecule(), linker_connectivity=2)

    assert linker.lines is not None
    assert len(linker.lines) > 0
    assert linker.fake_edge in (True, False)


@pytest.mark.core
def test_linker_create_public_api_with_injected_molecule():
    linker = FrameLinker()
    linker.linker_connectivity = 2
    linker.create(molecule=_ToyMolecule())

    assert linker.linker_center_data is not None
    assert linker.linker_center_X_data is not None
    assert linker.linker_center_attachment_data_by_type["X"].shape[0] == linker.linker_center_X_data.shape[0]
    assert linker.linker_center_data.shape[1] == 11


@pytest.mark.core
def test_linker_attachment_ordering_preserves_raw_order_without_metadata_rule():
    linker = FrameLinker()
    coords = {
        7: np.array([1.0, 0.0, 0.0]),
        3: np.array([0.0, 1.0, 0.0]),
        5: np.array([-1.0, 0.0, 0.0]),
    }

    records = linker._build_attachment_records([7, 3, 5], coords)
    ordered = linker._order_attachment_records(records, None, coords)

    assert [record["node_index"] for record in ordered] == [7, 3, 5]


@pytest.mark.core
def test_linker_clockwise_local_topology_reorders_and_emits_canonical_x_labels():
    linker = FrameLinker()
    linker.molecule_labels = []
    linker.molecule_coords = np.zeros((0, 3))
    linker.mass_center_angstrom = np.zeros(3)

    coords = {
        10: np.array([3.0, 0.0, 0.0]),
        20: np.array([0.0, 1.0, 0.0]),
        30: np.array([-1.0, 0.0, 0.0]),
        40: np.array([0.0, -1.0, 0.0]),
    }
    records = linker._build_attachment_records([20, 40, 10, 30], coords)
    order_rule = {
        "order_kind": "clockwise_local_topology",
        "ordered_attachment_indices": [0, 1, 2, 3],
    }

    ordered = linker._order_attachment_records(records, order_rule, coords)
    ordered_again = linker._order_attachment_records(records, order_rule, coords)
    ordered_node_ids = [record["node_index"] for record in ordered]

    assert ordered_node_ids == [record["node_index"] for record in ordered_again]
    assert set(ordered_node_ids) == {10, 20, 30, 40}
    assert ordered_node_ids != [20, 40, 10, 30]

    subgraph = nx.Graph()
    for node_idx in [30, 10, 40, 20]:
        subgraph.add_node(node_idx, label="C", coords=coords[node_idx])

    lines, x_rows = linker._lines_of_center_frag(subgraph, ordered_node_ids, [])

    assert x_rows == [0, 1, 2, 3]
    name_by_coord = {
        tuple(float(value) for value in line[2:5]): line[0]
        for line in lines
    }
    for expected_label, node_idx in enumerate(ordered_node_ids, start=1):
        coord_key = tuple(float(value) for value in coords[node_idx])
        assert name_by_coord[coord_key] == f"X{expected_label}"


@pytest.mark.core
def test_linker_lines_of_center_frag_uses_explicit_x_order_not_node_membership_order():
    linker = FrameLinker()
    linker.molecule_labels = []
    linker.molecule_coords = np.zeros((0, 3))
    linker.mass_center_angstrom = np.zeros(3)

    subgraph = nx.Graph()
    subgraph.add_node(5, label="C", coords=np.array([0.0, 0.0, 0.0]))
    subgraph.add_node(1, label="C", coords=np.array([1.0, 0.0, 0.0]))
    subgraph.add_node(9, label="C", coords=np.array([2.0, 0.0, 0.0]))

    lines, x_rows = linker._lines_of_center_frag(subgraph, [9, 5], [])

    assert x_rows == [0, 2]
    assert [line[0] for line in lines] == ["X2", "C2", "X1"]


@pytest.mark.core
def test_linker_attachment_ordering_rejects_unsupported_rule():
    linker = FrameLinker()
    coords = {
        1: np.array([1.0, 0.0, 0.0]),
        2: np.array([0.0, 1.0, 0.0]),
        3: np.array([-1.0, 0.0, 0.0]),
    }
    records = linker._build_attachment_records([1, 2, 3], coords)

    with pytest.raises(ValueError, match="Unsupported order_kind"):
        linker._order_attachment_records(
            records,
            {"order_kind": "unsupported", "ordered_attachment_indices": [0, 1, 2]},
            coords,
        )


@pytest.mark.core
def test_linker_attachment_ordering_rejects_metadata_length_mismatch():
    linker = FrameLinker()
    coords = {
        1: np.array([3.0, 0.0, 0.0]),
        2: np.array([0.0, 1.0, 0.0]),
        3: np.array([-1.0, 0.0, 0.0]),
        4: np.array([0.0, -1.0, 0.0]),
    }
    records = linker._build_attachment_records([1, 2, 3, 4], coords)

    with pytest.raises(ValueError, match="Attachment count does not match metadata rule"):
        linker._order_attachment_records(
            records,
            {
                "order_kind": "clockwise_local_topology",
                "ordered_attachment_indices": [0, 1, 2],
            },
            coords,
        )


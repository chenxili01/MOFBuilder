from pathlib import Path

import numpy as np
import pytest

from mofbuilder.io.cif_reader import CifReader
from mofbuilder.io.gro_reader import GroReader
from mofbuilder.io.pdb_reader import PdbReader
from mofbuilder.io.xyz_reader import XyzReader


TESTDATA = Path(__file__).resolve().parent / "testdata"


def write_test_cif(tmp_path, atom_lines, v_con=1, ec_con=None):
    header = "data_testnet  hall_number: 1, V_con: {}".format(v_con)
    if ec_con is not None:
        header += f", EC_con: {ec_con}"
    cif_lines = [
        header + "\n",
        "_symmetry_space_group_name_H-M    'P1'\n",
        "_symmetry_Int_Tables_number       1\n",
        "loop_\n",
        "_symmetry_equiv_pos_as_xyz\n",
        "  x,y,z\n",
        "_cell_length_a                    10.0\n",
        "_cell_length_b                    10.0\n",
        "_cell_length_c                    10.0\n",
        "_cell_angle_alpha                 90.0\n",
        "_cell_angle_beta                  90.0\n",
        "_cell_angle_gamma                 90.0\n",
        "loop_\n",
        "_atom_site_label\n",
        "_atom_site_type_symbol\n",
        "_atom_site_fract_x\n",
        "_atom_site_fract_y\n",
        "_atom_site_fract_z\n",
    ]
    cif_lines.extend(f"{line}\n" for line in atom_lines)
    cif_lines.append("loop_\n")
    cif_path = tmp_path / "topology.cif"
    cif_path.write_text("".join(cif_lines), encoding="utf-8")
    return cif_path


def test_xyz_reader_reads_and_recenters():
    reader = XyzReader(filepath=str(TESTDATA / "testlinker.xyz"))
    reader.read_xyz(recenter=True, com_type="C")

    assert reader.data is not None
    assert reader.data.shape[1] == 11
    coords = reader.data[:, 5:8].astype(float)
    c_mask = reader.data[:, 0] == "C"
    np.testing.assert_allclose(np.mean(coords[c_mask], axis=0), [0.0, 0.0, 0.0],
                               atol=1e-6)


def test_xyz_reader_missing_file_raises():
    reader = XyzReader(filepath="does_not_exist.xyz")
    with pytest.raises(FileNotFoundError):
        reader.read_xyz()


def test_pdb_reader_parses_node_and_extracts_x_atoms():
    reader = PdbReader(filepath=str(TESTDATA / "testnode.pdb"))
    reader.read_pdb(recenter=False)

    assert reader.data is not None
    assert reader.data.shape[1] == 11
    assert reader.X_data is not None
    assert len(reader.X_data) > 0


def test_pdb_reader_preserves_typed_attachment_groups(tmp_path):
    pdb_path = tmp_path / "typed_node.pdb"
    pdb_path.write_text(
        "".join([
            "HETATM    1 XA1  MOL A   1       0.000   0.000   0.000  1.00  0.00          C \n",
            "HETATM    2 XB1  MOL A   1       1.000   0.000   0.000  1.00  0.00          C \n",
            "HETATM    3 X1   MOL A   1       0.000   1.000   0.000  1.00  0.00          C \n",
            "HETATM    4 C1   MOL A   1       0.000   0.000   1.000  1.00  0.00          C \n",
        ]),
        encoding="utf-8",
    )

    reader = PdbReader(filepath=str(pdb_path))
    reader.read_pdb(recenter=False)

    assert set(reader.attachment_data_by_type) == {"X", "XA", "XB"}
    assert reader.attachment_data_by_type["XA"][0, 0] == "XA1"
    assert reader.attachment_data_by_type["XB"][0, 0] == "XB1"
    assert reader.X_data.shape[0] == 1


def test_pdb_reader_process_node_pdb_generates_centered_arrays():
    reader = PdbReader(filepath=str(TESTDATA / "testnode.pdb"))
    reader.process_node_pdb()

    assert reader.node_atoms is not None
    assert reader.node_ccoords is not None
    assert reader.node_x_ccoords is not None
    assert reader.node_ccoords.shape[1] == 3


def test_pdb_reader_process_node_pdb_preserves_typed_attachment_coords(tmp_path):
    pdb_path = tmp_path / "typed_centered_node.pdb"
    pdb_path.write_text(
        "".join([
            "HETATM    1 XA1  MOL A   1       0.000   0.000   0.000  1.00  0.00          C \n",
            "HETATM    2 XB1  MOL A   1       2.000   0.000   0.000  1.00  0.00          C \n",
            "HETATM    3 X1   MOL A   1       1.000   0.000   0.000  1.00  0.00          C \n",
            "HETATM    4 C1   MOL A   1       1.000   1.000   0.000  1.00  0.00          C \n",
        ]),
        encoding="utf-8",
    )

    reader = PdbReader(filepath=str(pdb_path))
    reader.com_target_type = "XA"
    reader.process_node_pdb()

    assert set(reader.node_attachment_ccoords_by_type) == {"X", "XA", "XB"}
    np.testing.assert_allclose(reader.node_attachment_ccoords_by_type["XA"], [[0.0, 0.0, 0.0]])
    np.testing.assert_allclose(reader.node_attachment_ccoords_by_type["XB"], [[2.0, 0.0, 0.0]])


def test_gro_reader_reads_writer_generated_file(tmp_path):
    gro_content = [
        f"{1:05d}{'MOL':<5}{'C1':>5}{1:5d}{0.100:8.3f}{0.200:8.3f}{0.300:8.3f}{'C':>2}\n",
        f"{1:05d}{'MOL':<5}{'O2':>5}{2:5d}{0.400:8.3f}{0.500:8.3f}{0.600:8.3f}{'O':>2}\n",
    ]
    gro_path = tmp_path / "mini.gro"
    gro_path.write_text("".join(gro_content), encoding="utf-8")

    reader = GroReader(filepath=str(gro_path))
    reader.read_gro()

    assert reader.data is not None
    assert reader.data.shape[1] == 11
    np.testing.assert_allclose(reader.data[0, 5:8].astype(float), [1.0, 2.0, 3.0])


def test_cif_reader_reads_cell_and_extracts_target_atoms():
    reader = CifReader(filepath=str(TESTDATA / "test.cif"))
    reader.read_cif()

    assert len(reader.cell_info) == 6
    cell_info, data, fcoords = reader.get_type_atoms_fcoords_in_primitive_cell(
        target_type="V")
    assert len(cell_info) == 6
    assert data is not None
    assert data.shape[1] == 11
    assert fcoords.shape[1] == 3


def test_cif_reader_missing_file_raises():
    reader = CifReader(filepath="missing.cif")
    with pytest.raises(AssertionError):
        reader.read_cif()


def test_cif_reader_preserves_raw_site_labels_for_role_parsing(tmp_path):
    cif_path = write_test_cif(
        tmp_path,
        [
            "VA1   V   0.2500  0.0000  0.0000",
            "VB1   V   0.7500  0.0000  0.0000",
            "EA1   E   0.0000  0.0000  0.0000",
        ],
    )
    reader = CifReader(filepath=str(cif_path))
    reader.read_cif()

    _, data, fcoords = reader.get_type_atoms_fcoords_in_primitive_cell(
        target_type="V")

    assert data.shape == (2, 11)
    assert reader.target_site_labels.tolist() == ["VA1", "VB1"]
    assert reader.target_role_labels.tolist() == ["VA", "VB"]
    np.testing.assert_allclose(fcoords, [[-0.25, 0.0, 0.0], [0.25, 0.0, 0.0]])

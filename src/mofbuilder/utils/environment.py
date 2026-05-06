from pathlib import Path


def get_data_path() -> Path:
    """Returns the path to the VeloxChem-hosted MOFBuilder database."""

    try:
        from ..vlx_compat import get_data_path as get_veloxchem_data_path

        data_path = Path(get_veloxchem_data_path())
        if (data_path / "MOF_topology_dict").exists():
            return data_path
    except (ImportError, ModuleNotFoundError):
        pass

    for parent in Path(__file__).resolve().parents:
        database = parent / "database"
        if (database / "MOF_topology_dict").exists():
            return database

    raise RuntimeError(
        "Unable to locate MOFBuilder database. Expected a VeloxChem database "
        "or a source-tree database directory containing MOF_topology_dict."
    )


if __name__ == "__main__":
    print(get_data_path())

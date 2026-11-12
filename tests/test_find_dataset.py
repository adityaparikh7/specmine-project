"""The scripts find the dataset wherever it is dragged inside data/."""
import pytest

from lib.io import TABLES, find_dataset_dir


def make_dataset(folder):
    folder.mkdir(parents=True)
    for table in TABLES:
        (folder / f"{table}.parquet").write_bytes(b"")


def test_finds_zenodo_folder_with_any_name(tmp_path):
    make_dataset(tmp_path / "SpecMine v1.0 (Zenodo)" / "data")
    assert find_dataset_dir(tmp_path) == tmp_path / "SpecMine v1.0 (Zenodo)" / "data"


def test_finds_loose_parquet_files(tmp_path):
    make_dataset(tmp_path / "raw")
    assert find_dataset_dir(tmp_path) == tmp_path / "raw"


def test_ignores_our_own_sample(tmp_path):
    make_dataset(tmp_path / "sample")
    make_dataset(tmp_path / "specmine")
    assert find_dataset_dir(tmp_path) == tmp_path / "specmine"


def test_no_dataset_explains_what_to_do(tmp_path):
    with pytest.raises(FileNotFoundError, match="drag"):
        find_dataset_dir(tmp_path)


def test_two_copies_is_an_error(tmp_path):
    make_dataset(tmp_path / "a")
    make_dataset(tmp_path / "b")
    with pytest.raises(RuntimeError, match="more than one"):
        find_dataset_dir(tmp_path)


def test_missing_table_is_named(tmp_path):
    make_dataset(tmp_path / "specmine")
    (tmp_path / "specmine" / "pr_files.parquet").unlink()
    with pytest.raises(FileNotFoundError, match="pr_files"):
        find_dataset_dir(tmp_path)

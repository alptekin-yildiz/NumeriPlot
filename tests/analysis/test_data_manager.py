import numpy as np
import pandas as pd

from src.analysis.data_manager import DataManager


def test_get_columns_returns_empty_when_no_data():
    manager = DataManager()
    assert manager.get_columns() == []


def test_load_file_csv_success_and_bom_column_cleanup(tmp_path):
    manager = DataManager()
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("\ufeffx,y\n1,2\n3,4\n", encoding="utf-8")

    ok, err = manager.load_file(str(csv_path))

    assert ok is True
    assert err is None
    assert manager.get_columns() == ["x", "y"]


def test_load_file_invalid_path_returns_error():
    manager = DataManager()
    ok, err = manager.load_file("/does/not/exist.csv")

    assert ok is False
    assert isinstance(err, str)
    assert err


def test_load_file_excel_branch_success(monkeypatch):
    manager = DataManager()

    def fake_read_excel(path):
        assert path.endswith(".xlsx")
        return pd.DataFrame({" a ": [1], " b ": [2]})

    monkeypatch.setattr(pd, "read_excel", fake_read_excel)

    ok, err = manager.load_file("dummy.xlsx")

    assert ok is True
    assert err is None
    assert manager.get_columns() == ["a", "b"]


def test_create_series_returns_none_when_no_dataframe():
    manager = DataManager()
    assert manager.create_series("x", "y") is None


def test_create_scatter_series_filters_non_numeric_rows():
    manager = DataManager()
    manager.df = pd.DataFrame({"x": [1, 2, "bad", 4], "y": [10, "bad", 30, 40]})

    series = manager.create_series("x", "y", plot_type="scatter")

    assert series is not None
    assert np.allclose(series["x"], np.array([1.0, 4.0]))
    assert np.allclose(series["y"], np.array([10.0, 40.0]))
    assert series["plot_type"] == "scatter"
    assert len(manager.series_list) == 1


def test_create_scatter_without_x_uses_1_based_index():
    manager = DataManager()
    manager.df = pd.DataFrame({"y": [1.0, np.nan, 5.0]})

    series = manager.create_series(None, "y")

    assert series is not None
    assert np.allclose(series["x"], np.array([1, 2]))
    assert np.allclose(series["y"], np.array([1.0, 5.0]))


def test_create_histogram_series_drops_nan_and_uses_defaults():
    manager = DataManager()
    manager.df = pd.DataFrame({"y": [1, "bad", 2, None, 3]})

    series = manager.create_series(None, "y", plot_type="histogram")

    assert series is not None
    assert np.allclose(series["y"], np.array([1.0, 2.0, 3.0]))
    assert series["bins"] == 20
    assert series["plot_type"] == "histogram"


def test_create_histogram_returns_none_when_all_values_invalid():
    manager = DataManager()
    manager.df = pd.DataFrame({"y": ["bad", None, np.nan]})

    series = manager.create_series(None, "y", plot_type="histogram")

    assert series is None


def test_create_bar_series_keeps_categories_and_filters_invalid_y():
    manager = DataManager()
    manager.df = pd.DataFrame({"cat": ["A", "B", "C"], "val": [1, "bad", 3]})

    series = manager.create_series("cat", "val", plot_type="bar")

    assert series is not None
    assert series["x"].tolist() == ["A", "C"]
    assert np.allclose(series["y"], np.array([1.0, 3.0]))
    assert series["plot_type"] == "bar"


def test_create_bar_returns_none_when_all_values_invalid():
    manager = DataManager()
    manager.df = pd.DataFrame({"cat": [None, None], "val": ["bad", np.nan]})

    series = manager.create_series("cat", "val", plot_type="bar")

    assert series is None


def test_create_scatter_returns_none_when_all_y_invalid():
    manager = DataManager()
    manager.df = pd.DataFrame({"x": [1, 2], "y": ["bad", None]})

    series = manager.create_series("x", "y", plot_type="scatter")

    assert series is None


def test_create_series_returns_none_on_internal_exception():
    manager = DataManager()
    manager.df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})

    series = manager.create_series("missing", "y", plot_type="bar")

    assert series is None


def test_panel_operations_clear_reassign_and_remove():
    manager = DataManager()
    manager.df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    manager.create_series("x", "y", panel_id=0)
    manager.create_series("x", "y", panel_id=1)

    manager.reassign_panel(old_panel_id=1, new_panel_id=2)
    assert len(manager.get_series_for_panel(2)) == 1

    moved = manager.reassign_orphan_series([2], target_panel_id=0)
    assert moved == 1
    assert len(manager.get_series_for_panel(0)) == 2

    manager.remove_series_from_panel(panel_id=0, local_index=0)
    assert len(manager.get_series_for_panel(0)) == 1

    manager.clear_panel(0)
    assert manager.get_series_for_panel(0) == []


def test_remove_series_and_get_all_series():
    manager = DataManager()
    manager.df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    manager.create_series("x", "y")
    manager.create_series("x", "y")

    all_series = manager.get_all_series()
    assert len(all_series) == 2

    manager.remove_series(0)
    assert len(manager.get_all_series()) == 1

    manager.remove_series(99)
    assert len(manager.get_all_series()) == 1

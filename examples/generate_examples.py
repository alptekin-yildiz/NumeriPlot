"""Generate deterministic, synthetic NumeriPlot example data and project."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.gaussian import DESCRIPTION_EN as GAUSSIAN_DESCRIPTION
from models.gaussian import PARAM_NAMES_EN as GAUSSIAN_PARAM_NAMES
from models.gaussian import model as gaussian_model
from models.lineer import model as linear_model
from models.tek_ustel_doyum import model as saturation_model
from src.project_schema import CURRENT_SCHEMA_VERSION


BASE_SEED = 20260830
CSV_FIELDS = ("x", "y", "y_error")

LINEAR_PARAMETERS = {"a": 2.5, "b": 1.2, "noise_sigma": 0.65}
GAUSSIAN_PARAMETERS = {
    "A": 8.0,
    "mu": 0.6,
    "sigma": 1.15,
    "noise_sigma": 0.18,
}
SATURATION_PARAMETERS = {
    "y0": 0.35,
    "A1": 4.8,
    "lambda1": 18.0,
    "noise_sigma": 0.08,
}


def build_datasets(base_seed: int = BASE_SEED) -> dict[str, dict[str, np.ndarray]]:
    """Return independent synthetic datasets derived from ``base_seed``."""
    x_linear = np.linspace(0.0, 10.0, 51)
    rng_linear = np.random.default_rng(base_seed)
    y_linear = linear_model(
        x_linear,
        LINEAR_PARAMETERS["a"],
        LINEAR_PARAMETERS["b"],
    ) + rng_linear.normal(0.0, LINEAR_PARAMETERS["noise_sigma"], x_linear.size)

    x_gaussian = np.linspace(-5.0, 5.0, 101)
    rng_gaussian = np.random.default_rng(base_seed + 1)
    y_gaussian = gaussian_model(
        x_gaussian,
        GAUSSIAN_PARAMETERS["A"],
        GAUSSIAN_PARAMETERS["mu"],
        GAUSSIAN_PARAMETERS["sigma"],
    ) + rng_gaussian.normal(
        0.0,
        GAUSSIAN_PARAMETERS["noise_sigma"],
        x_gaussian.size,
    )

    x_saturation = np.arange(0.0, 81.0, 1.0)
    rng_saturation = np.random.default_rng(base_seed + 2)
    y_saturation = saturation_model(
        x_saturation,
        SATURATION_PARAMETERS["y0"],
        SATURATION_PARAMETERS["A1"],
        SATURATION_PARAMETERS["lambda1"],
    ) + rng_saturation.normal(
        0.0,
        SATURATION_PARAMETERS["noise_sigma"],
        x_saturation.size,
    )

    return {
        "noisy_linear": {
            "x": x_linear,
            "y": y_linear,
            "y_error": np.full(x_linear.size, LINEAR_PARAMETERS["noise_sigma"]),
        },
        "gaussian_peak": {
            "x": x_gaussian,
            "y": y_gaussian,
            "y_error": np.full(x_gaussian.size, GAUSSIAN_PARAMETERS["noise_sigma"]),
        },
        "exponential_saturation": {
            "x": x_saturation,
            "y": y_saturation,
            "y_error": np.full(
                x_saturation.size,
                SATURATION_PARAMETERS["noise_sigma"],
            ),
        },
    }


def _csv_text(dataset: dict[str, np.ndarray]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(CSV_FIELDS)
    for values in zip(*(dataset[field] for field in CSV_FIELDS)):
        writer.writerow(f"{float(value):.8f}" for value in values)
    return stream.getvalue()


def _build_gaussian_project(
    dataset: dict[str, np.ndarray],
    raw_data: str,
    base_seed: int,
) -> dict:
    x = dataset["x"]
    y = dataset["y"]
    y_error = dataset["y_error"]

    popt, _pcov = curve_fit(
        gaussian_model,
        x,
        y,
        p0=[7.5, 0.5, 1.0],
        method="trf",
        maxfev=5000,
    )
    fit_x = np.linspace(float(x.min()), float(x.max()), 500)
    fit_y = gaussian_model(fit_x, *popt)
    residuals = y - gaussian_model(x, *popt)
    residual_mean = float(np.mean(residuals))
    residual_std = float(np.std(residuals, ddof=1))
    residual_rmse = float(np.sqrt(np.mean(residuals**2)))
    r2 = float(1.0 - np.sum(residuals**2) / np.sum((y - y.mean()) ** 2))

    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "raw_data": raw_data,
        "canvas_config": {
            "width_cm": 13.5,
            "height_cm": 8.5,
            "dpi": 150,
            "hspace": 0.4,
            "wspace": 0.3,
            "margin_left": 0.14,
            "margin_bottom": 0.14,
            "margin_right": 0.96,
            "margin_top": 0.92,
        },
        "layout": [1, 1],
        "panel_names": ["Gaussian Peak"],
        "panel_configs": [
            {
                "title": "Synthetic Gaussian Peak and Fit",
                "xlabel": "x (arbitrary units)",
                "ylabel": "Signal (arbitrary units)",
                "fontfamily": "DejaVu Sans",
                "size_title": 13,
                "size_label": 11,
                "size_tick": 10,
                "grid": True,
                "grid_style": ":",
                "grid_alpha": 0.35,
                "legend_show": True,
                "legend_loc": "upper right",
                "legend_frame": True,
                "legend_fontsize": 9,
            }
        ],
        "series": [
            {
                "label": "Synthetic observations",
                "x": x.tolist(),
                "y": y.tolist(),
                "x_col": "x",
                "y_col": "y",
                "axis": "left",
                "plot_type": "scatter",
                "color": "#2f6f9f",
                "marker": "o",
                "linestyle": "None",
                "filled": True,
                "markersize": 4.0,
                "markeredgewidth": 0.5,
                "linewidth": 1.0,
                "capsize": 2.0,
                "elinewidth": 0.8,
                "ecolor": "#7aa6c2",
                "alpha": 0.9,
                "interpolation": "linear",
                "x_err": None,
                "y_err": y_error.tolist(),
                "panel_id": 0,
                "legend_show": True,
                "legend_label": "Synthetic observations",
                "legend_order": 0,
            }
        ],
        "fits": [
            {
                "label": "Fit: Gaussian Distribution",
                "x": fit_x.tolist(),
                "y": fit_y.tolist(),
                "color": "#c33d3d",
                "axis": "left",
                "panel_id": 0,
                "linewidth": 1.8,
                "linestyle": "-",
                "marker": "None",
                "markersize": 0,
                "model_name": "Gaussian Distribution",
                "model_description": GAUSSIAN_DESCRIPTION,
                "param_names": GAUSSIAN_PARAM_NAMES,
                "param_values": [float(value) for value in popt],
                "source_series": "Synthetic observations",
                "res_x": x.tolist(),
                "res_y": residuals.tolist(),
                "r2": r2,
                "res_stats": {
                    "n": int(residuals.size),
                    "mean": residual_mean,
                    "std": residual_std,
                    "rmse": residual_rmse,
                },
            }
        ],
        "text_items": [
            {
                "id": 1,
                "panel_id": 0,
                "text": f"Synthetic data only · seed {base_seed + 1}",
                "coord_mode": "axes",
                "x": 0.02,
                "y": 0.04,
                "ha": "left",
                "va": "bottom",
                "fontsize": 8,
                "fontfamily": "DejaVu Sans",
                "bold": False,
                "italic": True,
                "math_mode": False,
                "rotation": 0.0,
                "color": "#555555",
            }
        ],
        "text_auto_cfg": {"enabled": False},
        "global_states": {},
    }


def generate_examples(
    output_root: Path | str = Path(__file__).resolve().parent,
    base_seed: int = BASE_SEED,
) -> list[Path]:
    """Write all tracked example artifacts and return their paths."""
    output_root = Path(output_root)
    data_dir = output_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    datasets = build_datasets(base_seed)
    written = []
    csv_payloads = {}
    for name, dataset in datasets.items():
        payload = _csv_text(dataset)
        path = data_dir / f"{name}.csv"
        path.write_text(payload, encoding="utf-8", newline="")
        written.append(path)
        csv_payloads[name] = payload

    project = _build_gaussian_project(
        datasets["gaussian_peak"],
        csv_payloads["gaussian_peak"],
        base_seed,
    )
    project_path = output_root / "NumeriPlot_example_project.json"
    project_path.write_text(
        json.dumps(project, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    written.append(project_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory that will contain data/ and the example project.",
    )
    parser.add_argument("--seed", type=int, default=BASE_SEED)
    args = parser.parse_args()

    for path in generate_examples(args.output_root, args.seed):
        print(path.relative_to(args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

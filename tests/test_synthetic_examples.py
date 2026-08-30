import json
from pathlib import Path

import numpy as np
from PIL import Image

from examples.generate_examples import (
    GAUSSIAN_PARAMETERS,
    LINEAR_PARAMETERS,
    SATURATION_PARAMETERS,
    build_datasets,
    generate_examples,
)
from models.gaussian import model as gaussian_model
from models.lineer import model as linear_model
from models.tek_ustel_doyum import model as saturation_model


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
SCREENSHOTS = ROOT / "assets" / "screenshots"


def test_generated_outputs_match_tracked_examples(tmp_path):
    generate_examples(tmp_path)

    relative_paths = (
        "data/noisy_linear.csv",
        "data/gaussian_peak.csv",
        "data/exponential_saturation.csv",
        "NumeriPlot_example_project.json",
    )
    for relative_path in relative_paths:
        assert (tmp_path / relative_path).read_bytes() == (
            EXAMPLES / relative_path
        ).read_bytes()


def test_synthetic_noise_matches_documented_models():
    datasets = build_datasets()
    cases = (
        (
            datasets["noisy_linear"],
            linear_model,
            (LINEAR_PARAMETERS["a"], LINEAR_PARAMETERS["b"]),
        ),
        (
            datasets["gaussian_peak"],
            gaussian_model,
            (
                GAUSSIAN_PARAMETERS["A"],
                GAUSSIAN_PARAMETERS["mu"],
                GAUSSIAN_PARAMETERS["sigma"],
            ),
        ),
        (
            datasets["exponential_saturation"],
            saturation_model,
            (
                SATURATION_PARAMETERS["y0"],
                SATURATION_PARAMETERS["A1"],
                SATURATION_PARAMETERS["lambda1"],
            ),
        ),
    )

    for dataset, model, parameters in cases:
        standardized_noise = (
            dataset["y"] - model(dataset["x"], *parameters)
        ) / dataset["y_error"]
        assert abs(float(np.mean(standardized_noise))) < 0.3
        assert 0.7 < float(np.std(standardized_noise, ddof=1)) < 1.3


def test_example_project_is_synthetic_and_contains_fit_results():
    project_path = EXAMPLES / "NumeriPlot_example_project.json"
    raw = project_path.read_text(encoding="utf-8")
    project = json.loads(raw)

    assert project["schema_version"] == "1.0"
    assert "version" not in project
    assert project["raw_data"].startswith("x,y,y_error\n")
    assert project["series"][0]["label"] == "Synthetic observations"
    assert project["fits"][0]["model_name"] == "Gaussian Distribution"
    assert project["fits"][0]["r2"] > 0.98
    assert "Synthetic data only" in project["text_items"][0]["text"]
    assert "/Users/" not in raw
    assert "OneDrive" not in raw


def test_screenshots_have_expected_size_and_no_path_metadata():
    for name in ("numeriplot-overview.png", "numeriplot-fit-analysis.png"):
        with Image.open(SCREENSHOTS / name) as image:
            assert image.size == (1440, 900)
            metadata = repr(image.info)
            assert "/Users/" not in metadata
            assert "OneDrive" not in metadata

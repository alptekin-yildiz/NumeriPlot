import numpy as np
import pandas as pd

from lang import t


def prepare_fit_xy(x_values, y_values) -> tuple[np.ndarray, np.ndarray]:
    """
    Fit için X/Y vektörlerini güvenli şekilde hazırlar.

    Kurallar:
    - Y her zaman sayısala çevrilir.
    - X yoksa veya boyutu Y ile uyuşmuyorsa otomatik 1..n üretilir.
    - NaN değerler temizlenir.
    - Sonsuz değerler reddedilir; sessizce nokta çıkarılmaz.
    - En az iki geçerli nokta yoksa ValueError fırlatılır.
    """
    raw_x = np.asarray(x_values if x_values is not None else [])
    raw_y = np.asarray(y_values if y_values is not None else [])

    y_num = pd.to_numeric(pd.Series(raw_y), errors="coerce").to_numpy(dtype=float)
    if y_num.size == 0:
        raise ValueError(t("fit_insufficient_data"))
    if np.isinf(y_num).any():
        raise ValueError(t("fit_nonfinite_data"))

    use_auto_x = not (raw_x.size > 0 and raw_x.size == y_num.size)
    if use_auto_x:
        mask = ~np.isnan(y_num)
        y = y_num[mask]
        x = np.arange(1, y.size + 1, dtype=float)
    else:
        x_num = pd.to_numeric(pd.Series(raw_x), errors="coerce").to_numpy(dtype=float)
        if np.isinf(x_num).any():
            raise ValueError(t("fit_nonfinite_data"))
        mask = ~np.isnan(y_num) & ~np.isnan(x_num)
        x = x_num[mask]
        y = y_num[mask]

    if x.size < 2 or y.size < 2:
        raise ValueError(t("fit_insufficient_data"))

    return x, y


def evaluate_fit_model(func, x, parameters):
    """Reject invalid model evaluations before they can enter a saved fit."""
    try:
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            values = np.asarray(func(x, *parameters), dtype=float)
        if values.shape != np.shape(x) or not np.isfinite(values).all():
            raise ValueError(t("fit_invalid_result"))
    except (FloatingPointError, OverflowError, ZeroDivisionError) as error:
        raise ValueError(t("fit_invalid_result")) from error
    return values


def fit_statistics(y, predicted):
    """Residual statistics; R² is undefined (None) for constant observations."""
    y = np.asarray(y, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if (y.ndim != 1 or y.size < 2 or predicted.shape != y.shape
            or not np.isfinite(y).all() or not np.isfinite(predicted).all()):
        raise ValueError(t("fit_invalid_result"))
    try:
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            residuals = y - predicted
            squared_error = np.sum(residuals ** 2)
            r2 = None if np.all(y == y[0]) else float(
                1 - squared_error / np.sum((y - y.mean()) ** 2)
            )
            stats = {
                "n": int(y.size),
                "mean": float(np.mean(residuals)),
                "std": float(np.std(residuals, ddof=1)),
                "rmse": float(np.sqrt(squared_error / y.size)),
            }
        if not all(np.isfinite(value) for value in stats.values()) or (
                r2 is not None and not np.isfinite(r2)):
            raise ValueError(t("fit_invalid_result"))
    except FloatingPointError as error:
        raise ValueError(t("fit_invalid_result")) from error
    return residuals, r2, stats

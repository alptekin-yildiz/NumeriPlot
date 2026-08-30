import numpy as np
import pandas as pd


def prepare_fit_xy(x_values, y_values) -> tuple[np.ndarray, np.ndarray]:
    """
    Fit için X/Y vektörlerini güvenli şekilde hazırlar.

    Kurallar:
    - Y her zaman sayısala çevrilir.
    - X yoksa veya boyutu Y ile uyuşmuyorsa otomatik 1..n üretilir.
    - NaN değerler temizlenir.
    - En az iki geçerli nokta yoksa ValueError fırlatılır.
    """
    raw_x = np.asarray(x_values if x_values is not None else [])
    raw_y = np.asarray(y_values if y_values is not None else [])

    y_num = pd.to_numeric(pd.Series(raw_y), errors="coerce").to_numpy(dtype=float)
    if y_num.size == 0:
        raise ValueError("Fit için geçerli Y verisi yok.")

    use_auto_x = not (raw_x.size > 0 and raw_x.size == y_num.size)
    if use_auto_x:
        mask = ~np.isnan(y_num)
        y = y_num[mask]
        x = np.arange(1, y.size + 1, dtype=float)
    else:
        x_num = pd.to_numeric(pd.Series(raw_x), errors="coerce").to_numpy(dtype=float)
        mask = ~np.isnan(y_num) & ~np.isnan(x_num)
        x = x_num[mask]
        y = y_num[mask]

    if x.size < 2 or y.size < 2:
        raise ValueError("Fit için en az 2 geçerli veri noktası gerekir.")

    return x, y

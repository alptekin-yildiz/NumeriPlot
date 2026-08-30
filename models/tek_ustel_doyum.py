import numpy as np

NAME = "Tek Üstel Doyum"
DESCRIPTION = "y(n) = y₀ + A₁·(1 - exp(-n/λ₁))  |  Taban (y₀), genlik (A₁) ve karakteristik çevrim (λ₁)"
PARAM_NAMES = ["y₀ (Taban)", "A₁ (Genlik)", "λ₁ (Karakteristik Çevrim)"]

NAME_EN = "Single Exponential Saturation"
DESCRIPTION_EN = "y(n) = y₀ + A₁·(1 - exp(-n/λ₁))  |  Baseline (y₀), amplitude (A₁), and characteristic cycle (λ₁)"
PARAM_NAMES_EN = ["y₀ (Baseline)", "A₁ (Amplitude)", "λ₁ (Characteristic Cycle)"]


def model(n, y0, A1, lambda1):
    lam = float(lambda1)
    if abs(lam) < 1e-12:
        lam = 1e-12
    return y0 + A1 * (1.0 - np.exp(-np.asarray(n, dtype=float) / lam))

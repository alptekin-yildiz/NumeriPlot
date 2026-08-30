import numpy as np

NAME = "Üstel Bozunma"
DESCRIPTION = "y = A·exp(-x/τ) + y₀  |  Genlik (A), zaman sabiti (τ) ve taban değer (y₀)"
PARAM_NAMES = ["A (Genlik)", "τ (Zaman Sabiti)", "y₀ (Taban)"]

NAME_EN = "Exponential Decay"
DESCRIPTION_EN = "y = A·exp(-x/τ) + y₀  |  Amplitude (A), time constant (τ) and offset (y₀)"
PARAM_NAMES_EN = ["A (Amplitude)", "τ (Time Constant)", "y₀ (Offset)"]

def model(x, A, tau, y0):
    return A * np.exp(-x / tau) + y0

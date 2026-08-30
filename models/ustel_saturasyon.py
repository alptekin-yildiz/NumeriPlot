import numpy as np

NAME = "Üstel Doyum"
DESCRIPTION = "y = A - B·(x+1)⁻ᵏ  |  Doyum limiti (A), ölçek (B) ve hız üssü (k)"
PARAM_NAMES = ["A (Doyum Limiti)", "B (Ölçek)", "k (Hız Üssü)"]

NAME_EN = "Exponential Saturation"
DESCRIPTION_EN = "y = A - B·(x+1)⁻ᵏ  |  Saturation limit (A), scale (B) and rate exponent (k)"
PARAM_NAMES_EN = ["A (Saturation Limit)", "B (Scale)", "k (Rate Exponent)"]

def model(x, A, B, k):
    return A - B * np.power(x + 1, -k)

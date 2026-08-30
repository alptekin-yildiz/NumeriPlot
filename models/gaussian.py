import numpy as np

NAME = "Gauss Dağılımı"
DESCRIPTION = "y = A·exp(-(x-μ)²/2σ²)  |  Pik yüksekliği (A), merkez (μ) ve genişlik (σ)"
PARAM_NAMES = ["A (Yükseklik)", "μ (Merkez)", "σ (Genişlik)"]

NAME_EN = "Gaussian Distribution"
DESCRIPTION_EN = "y = A·exp(-(x-μ)²/2σ²)  |  Peak height (A), center (μ) and width (σ)"
PARAM_NAMES_EN = ["A (Height)", "μ (Center)", "σ (Width)"]

def model(x, A, mu, sigma):
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2))

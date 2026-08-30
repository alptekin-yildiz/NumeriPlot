import numpy as np

NAME = "Güç Yasası"
DESCRIPTION = "y = K·xⁿ  |  Kıvam indeksi (K) ve akış indeksi (n)"
PARAM_NAMES = ["K (Kıvam İndeksi)", "n (Akış İndeksi)"]

NAME_EN = "Power Law"
DESCRIPTION_EN = "y = K·xⁿ  |  Consistency index (K) and flow index (n)"
PARAM_NAMES_EN = ["K (Consistency Index)", "n (Flow Index)"]

def model(x, K, n):
    return K * np.power(x, n)

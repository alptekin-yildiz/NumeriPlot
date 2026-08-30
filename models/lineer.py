import numpy as np

NAME = "Doğrusal"
DESCRIPTION = "y = a·x + b  |  Eğim (a) ve kesen (b) parametreli basit doğrusal fit"
PARAM_NAMES = ["a (Eğim)", "b (Kesen)"]

NAME_EN = "Linear"
DESCRIPTION_EN = "y = a·x + b  |  Simple linear fit with slope (a) and intercept (b)"
PARAM_NAMES_EN = ["a (Slope)", "b (Intercept)"]

def model(x, a, b):
    return a * x + b

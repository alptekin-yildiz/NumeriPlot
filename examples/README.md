# NumeriPlot synthetic examples

Every file in this directory is generated from formulas and contains synthetic
data only. No research, student, patient, or personal data is included.

Regenerate the CSV files and example project from the repository root:

```bash
python3 examples/generate_examples.py
```

The generator uses independent deterministic NumPy random streams derived from
the base seed `20260830` and writes values with eight decimal places.

## Datasets

| File | Formula | Parameters | Noise σ |
| --- | --- | --- | ---: |
| `data/noisy_linear.csv` | `y = a*x + b + ε` | `a = 2.5`, `b = 1.2` | 0.65 |
| `data/gaussian_peak.csv` | `y = A*exp(-(x-mu)^2/(2*sigma^2)) + ε` | `A = 8.0`, `mu = 0.6`, `sigma = 1.15` | 0.18 |
| `data/exponential_saturation.csv` | `y = y0 + A1*(1-exp(-n/lambda1)) + ε` | `y0 = 0.35`, `A1 = 4.8`, `lambda1 = 18.0` | 0.08 |

In every case `ε` is independent zero-mean Gaussian noise. The `y_error`
column records the standard deviation used to generate that dataset.

`NumeriPlot_example_project.json` uses the Gaussian dataset and includes a
Gaussian fit, residual statistics, display settings, and an explicit
synthetic-data annotation. It uses NumeriPlot project schema 1.0 and is checked
by the automated project-open and round-trip tests.

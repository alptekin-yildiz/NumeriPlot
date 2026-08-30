---
name: Fit model proposal
about: Propose a scientifically documented fitting model
title: "[Fit model]: "
labels: ""
assignees: ""
---

A fit model proposal must be independently reviewable before implementation.
Do not include sensitive data or a vulnerability; follow
[`SECURITY.md`](../../SECURITY.md) for private security reports. Use synthetic
or otherwise redistributable validation material.

### Model name

<!-- Include suggested English and Turkish display names when possible. -->

### Equation

<!-- Define the model unambiguously and explain every symbol. -->

### Parameter names and physical meanings

<!-- List each parameter, its meaning, units or dimensions, and sign constraints. -->

### Valid data domain

<!-- State valid x/y ranges, units, exclusions, and mathematical singularities. -->

### Initial values and bounds

<!-- Suggest defaults or estimation rules and justified parameter bounds. -->

### Numerical behavior

<!-- Note scaling, convergence, identifiability, overflow, or conditioning risks. -->

### Scientific reference

<!-- Cite a stable source that defines or validates the model. -->

### Validation data

<!--
Provide synthetic or otherwise redistributable data plus independently
checkable expected parameters or predictions.
-->

### Expected tolerance

<!-- State absolute and/or relative tolerances and explain why they are appropriate. -->

### Licensing and provenance

<!-- Confirm that equations, reference material, and validation data may be used. -->

### Checklist

- [ ] The equation and every parameter are defined.
- [ ] The valid domain, initial values, and bounds are documented.
- [ ] A scientific reference and reproducible validation case are provided.
- [ ] Validation material is synthetic or safely redistributable.
- [ ] This is not a security report that belongs in `SECURITY.md`.

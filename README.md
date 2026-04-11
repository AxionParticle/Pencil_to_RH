# Pencil Code → RH 1.5D Pipeline

This repository provides a pipeline to convert 3D MHD simulation data from the Pencil Code into column-by-column input suitable for the RH 1.5D radiative transfer code.

It is designed for studying radiative transfer in solar/astrophysical atmospheres, including spectral line formation such as Hα and continuum diagnostics.

---

## 🔬 Overview

The Pencil Code produces fully compressible MHD simulations in 3D. However, the RH 1.5D code operates in a 1.5D framework, requiring independent vertical columns as input.

This pipeline:

* Reads Pencil Code simulation snapshots
* Extracts physical variables (e.g., density, temperature, velocity)
* Converts them into RH 1.5D-compatible atmospheric columns
* Processes multiple snapshots efficiently
* Provides visualization tools for validation

---

## 📂 Repository Structure

```
pencil-to-rh/
│
├── scripts/              # Core processing scripts
│   ├── read_pencil.py
│   ├── convert_to_rh.py
│   └── plot_results.py
│
├── notebooks/            # (Recommended to use) Jupyter notebooks
├── data/                 # Pencil Code outputs
├── output/               # RH results
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

Main libraries:

* numpy
* matplotlib
* h5py
* xarray
* Pencil Code Python tools

---

## 🚀 Usage

### 1. Read Pencil Code Data

```bash
python scripts/read_pencil.py
```

### 2. Convert to RH Input Format

```bash
python scripts/convert_to_rh.py
```

### 3. Plot / Validate Results

```bash
python scripts/plot_results.py
```

---

## 📊 Output

The pipeline generates:

* Column-by-column atmospheric models for RH 1.5D
* Derived quantities such as:

  * Optical depth (τ)
  * τ = 1 height maps
* Visualization plots for sanity checks

---

## 🧠 Scientific Context

This work is relevant for:

* Solar chromosphere forward modeling
* Radiative transfer in MHD simulations
* Spectral line formation (e.g., Hα)
* Coupling MHD simulations with radiative diagnostics

---

## ⚠️ Notes

* Large simulation data is not included in this repository.
* Ensure correct units and normalization when converting variables.
* RH 1.5D requires careful formatting of atmospheric inputs — verify outputs before running radiative transfer.

---

## 👤 Author

Sanket Wavhal
Integrated B.Tech + M.Tech (Engineering Physics)
IIT (BHU), Varanasi
Email: wavhal.sankets.phy20@itbhu.ac.in , sanketwavhal7@gmail.com 

---

## 📜 License

This project is open for academic and research use.

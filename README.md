# Pencil Code → RH Pipeline (1.5D & 3D)

This repository provides a modular pipeline to convert 3D MHD simulation data from the Pencil Code into input suitable for the RH radiative transfer code.

It supports both:

* **RH 1.5D** (column-by-column radiative transfer)
* **RH 3D (XDR format)** for full atmosphere cubes

The pipeline is designed for solar and astrophysical applications, including spectral line formation (e.g., Hα) and chromospheric diagnostics.

---

## 🔬 Overview

The Pencil Code produces fully compressible 3D MHD simulations. Radiative transfer modeling with RH requires structured atmospheric input:

* **RH 1.5D** → independent vertical columns
* **RH 3D** → full 3D atmosphere cube (XDR format)

This repository bridges that gap.

### Features

* Read Pencil Code snapshots (`var` files)
* Convert simulation units → physical units
* Extract atmospheric variables:

  * Temperature (T)
  * Density (ρ)
  * Velocity (vx, vy, vz)
  * Ionization fraction (yH)
* Compute:

  * Electron density (ne)
  * Hydrogen populations (nH⁰, nH⁺)
* Height filtering and subcube extraction
* RH-compatible output:

  * HDF5 (1.5D)
  * XDR (3D)
* Validation plots (2D + 1D)

---

## 📂 Repository Structure

```id="tree1"
pencil-to-rh/
│
├── scripts/
│   ├── read_pencil.py          # Read + validate Pencil data
│   ├── convert_to_rh.py        # RH 1.5D (HDF5)
│   ├── convert_to_rh_3d.py     # RH 3D (XDR)
│   └── plot_results.py         # Visualization tools
│
├── notebooks/                  # Recommended
├── data/                       # Pencil outputs
├── output/                     # RH outputs
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

### Main libraries

* numpy
* matplotlib
* h5py
* scipy
* xdrlib3
* Pencil Code Python tools

> Pencil Code tools must be installed separately from source.

---

## 🚀 Usage

### 1. Read and validate Pencil data

```bash
python scripts/read_pencil.py
```

Generates:

* 2D slices
* 1D vertical profiles
* sanity checks for T, ne, velocity

---

### 2. Convert to RH 1.5D (HDF5)

```bash
python scripts/convert_to_rh.py
```

Output:

```
output/rh_atmosphere.hdf5
```

---

### 3. Convert to RH 3D (XDR)

```bash
python scripts/convert_to_rh_3d.py
```

Output:

```
output/rh_3d.atmos
```

Features:

* Optional height filtering
* Optional subcube extraction
* Full 3D atmosphere preserved
* 2-level hydrogen populations

---

### 4. Plot RH results

```bash
python scripts/plot_results.py
```

---

## 📊 Output Description

### RH 1.5D (HDF5)

* Temperature
* Electron density
* Velocity (vz)
* Hydrogen populations
* Grid coordinates (x, y, z)

### RH 3D (XDR)

* Full 3D cube:

  * T(x,y,z)
  * ne(x,y,z)
  * v(x,y,z)
  * nH⁰, nH⁺
* Grid spacing and height scale
* Compatible with RH 3D setup

---

## ⚙️ Configuration (3D pipeline)

Inside `convert_to_rh_3d.py`:

```python
USE_HEIGHT_FILTER = True
USE_SUBCUBE = True
```

### Height filtering

```python
Z_MIN = -0.3e6
Z_MAX = 15e6
```

### Subcube selection

```python
X_RANGE = (80, 112, 1)
Y_RANGE = (80, 112, 1)
```

---

## 🧠 Scientific Context

This pipeline is relevant for:

* Solar chromosphere modelling
* Radiative transfer in MHD simulations
* Spectral line formation (e.g., Hα)
* Coupling numerical simulations with radiative diagnostics

---

## ⚠️ Important Notes

* Large simulation data is **not included** in this repository
* Ensure consistent units during conversion
* RH requires:

  * Correct ordering (top → observer)
  * Proper normalisation of populations

### RH 3D considerations

* Computationally expensive (memory-heavy)
* Often used with reduced domains (subcubes)
* May still assume column-wise radiative transfer depending on the setup

---

## 🔬 Limitations / Future Work

* Hydrogen is treated as a **2-level atom**
* No multi-level NLTE populations yet
* No spectral synthesis included (e.g., Hα intensity)

### Planned extensions

* τ = 1 height maps
* Multi-level hydrogen atom
* Spectral synthesis (RH outputs → intensity)
* Batch processing of multiple snapshots

---

## 👤 Author

**Sanket Wavhal**
Integrated B.Tech + M.Tech (Engineering Physics)
IIT (BHU), Varanasi

Email:
[wavhal.sankets.phy20@itbhu.ac.in](mailto:wavhal.sankets.phy20@itbhu.ac.in)
[sanketwavhal7@gmail.com](mailto:sanketwavhal7@gmail.com)

---

## 📜 License

This project is intended for academic and research use.

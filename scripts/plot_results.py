"""
plot_results.py

Read RH output file and generate validation plots.

Author: Sanket Wavhal
"""

# ------------------------------------------------------------
# IMPORT LIBRARIES
# ------------------------------------------------------------
import h5py
import numpy as np
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------
INPUT_FILE = "../output/rh_atmosphere.hdf5"


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
def load_rh_file(filename):
    """Load RH atmosphere file."""

    with h5py.File(filename, "r") as f:
        T  = f["temperature"][:]
        vz = f["velocity_z"][:]
        ne = f["electron_density"][:]
        z  = f["z"][:]

    return T, vz, ne, z


# ------------------------------------------------------------
# PLOT
# ------------------------------------------------------------
def plot_results(T, vz, ne, z):
    """Plot RH data (2D + 1D)."""

    nt, nx, ny, nz = T.shape

    ix = nx // 2
    iy = ny // 2

    cmap = plt.get_cmap('gist_rainbow')

    print("Plotting RH results...")

    # ----------------------------
    # 2D
    # ----------------------------
    plt.figure()
    plt.imshow(T[0, ix, :, :].T, origin='lower', aspect='auto', cmap=cmap)
    plt.colorbar(label="Temperature (K)")
    plt.title("Temperature (RH 2D)")
    plt.show()

    plt.figure()
    plt.imshow(ne[0, ix, :, :].T, origin='lower', aspect='auto', cmap=cmap)
    plt.colorbar(label="Electron Density (m^-3)")
    plt.title("Electron Density (RH 2D)")
    plt.show()

    plt.figure()
    plt.imshow(vz[0, ix, :, :].T, origin='lower', aspect='auto', cmap=cmap)
    plt.colorbar(label="Vz (m/s)")
    plt.title("Velocity (RH 2D)")
    plt.show()

    # ----------------------------
    # 1D
    # ----------------------------
    plt.figure()
    plt.plot(T[0, ix, iy, :], z[0, :])
    plt.title("Temperature (RH 1D)")
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(ne[0, ix, iy, :], z[0, :])
    plt.title("Electron Density (RH 1D)")
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(vz[0, ix, iy, :], z[0, :])
    plt.title("Velocity (RH 1D)")
    plt.grid()
    plt.show()


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():

    T, vz, ne, z = load_rh_file(INPUT_FILE)

    print(f"Loaded RH file: {INPUT_FILE}")
    print(f"Shape: {T.shape}")

    plot_results(T, vz, ne, z)


if __name__ == "__main__":
    main()
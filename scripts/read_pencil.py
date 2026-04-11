"""
read_pencil.py

Read Pencil Code snapshot (var file), convert physical variables,
apply height filtering, and generate validation plots.

Author: Sanket Wavhal
"""

# ------------------------------------------------------------
# IMPORT LIBRARIES
# ------------------------------------------------------------
import pencil as pc
import numpy as np
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------
DATADIR = "../data"
IVAR = 109          # example file

Z_MIN = -0.3e6      # m
Z_MAX = 15e6        # m


# ------------------------------------------------------------
# READ DATA
# ------------------------------------------------------------
def read_pencil_data(datadir, ivar):
    """Read Pencil Code snapshot and parameters."""
    
    print("Reading Pencil Code data...")
    
    param = pc.read.param(datadir=datadir)

    var = pc.read.varraw(
        ivar=ivar,
        var_list=['uu', 'lnrho', 'lnTT', 'yH'],
        datadir=datadir,
        trimall=True
    )               # trimall removes ghost zones

    print("Variables loaded (ghost zones removed).")
    
    return param, var


# ------------------------------------------------------------
# CONVERT VARIABLES
# ------------------------------------------------------------
def convert_variables(param, var):
    """Convert code units to physical units."""

    T   = np.exp(var.lnTT) * param.unit_temperature      # K
    rho = np.exp(var.lnrho) * param.unit_density * 1000  # kg/m^3
    vz  = var.uz * param.unit_velocity * 1e-2            # m/s
    yH  = var.yH

    return T, rho, vz, yH


# ------------------------------------------------------------
# RECONSTRUCT HEIGHT
# ------------------------------------------------------------
def compute_height(param, nz):
    """Reconstruct z-grid."""
    
    z = np.linspace(param.xyz0[2], param.xyz1[2], nz)
    z = z * param.unit_length * 1e-2  # cm → m
    
    return z


# ------------------------------------------------------------
# HEIGHT FILTER
# ------------------------------------------------------------
def apply_height_filter(z, T, rho, vz, yH, z_min, z_max):
    """Apply height cut."""
    
    mask = (z >= z_min) & (z <= z_max)

    z   = z[mask]
    T   = T[:, :, mask]
    rho = rho[:, :, mask]
    vz  = vz[:, :, mask]
    yH  = yH[:, :, mask]

    return z, T, rho, vz, yH


# ------------------------------------------------------------
# ELECTRON DENSITY
# ------------------------------------------------------------
def compute_electron_density(rho, yH):
    """Compute electron density."""
    
    xH  = 1.0
    xHe = 0.081
    mp  = 1.6726219e-27

    mu0 = 1 + 4 * xHe
    mu  = mu0 / (1 + yH * xH)

    n_total = rho / (mu * mp)
    ne      = yH * n_total

    return ne


# ------------------------------------------------------------
# PLOTTING
# ------------------------------------------------------------
def plot_validation(T, ne, vz, z):
    """Generate 2D and 1D validation plots."""
    
    nx, ny, nz = T.shape
    ix = nx // 2
    iy = ny // 2

    cmap = plt.get_cmap('gist_rainbow')

    print("Generating plots...")

    # ----------------------------
    # 2D PLOTS
    # ----------------------------
    plt.figure()
    plt.imshow(T[ix, :, :].T, origin='lower', aspect='auto', cmap=cmap)
    plt.colorbar(label="Temperature (K)")
    plt.title("Temperature (2D)")
    plt.show()

    plt.figure()
    plt.imshow(ne[ix, :, :].T, origin='lower', aspect='auto', cmap=cmap)
    plt.colorbar(label="Electron Density (m^-3)")
    plt.title("Electron Density (2D)")
    plt.show()

    plt.figure()
    plt.imshow(vz[ix, :, :].T, origin='lower', aspect='auto', cmap=cmap)
    plt.colorbar(label="Vz (m/s)")
    plt.title("Velocity (2D)")
    plt.show()

    # ----------------------------
    # 1D PLOTS
    # ----------------------------
    plt.figure()
    plt.plot(T[ix, iy, :], z)
    plt.xlabel("T (K)")
    plt.ylabel("z (m)")
    plt.title("Temperature (1D)")
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(ne[ix, iy, :], z)
    plt.xlabel("ne (m^-3)")
    plt.ylabel("z (m)")
    plt.title("Electron Density (1D)")
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(vz[ix, iy, :], z)
    plt.xlabel("vz (m/s)")
    plt.ylabel("z (m)")
    plt.title("Velocity (1D)")
    plt.grid()
    plt.show()


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    
    # Read data
    param, var = read_pencil_data(DATADIR, IVAR)

    # Convert variables
    T, rho, vz, yH = convert_variables(param, var)

    nx, ny, nz = T.shape
    print(f"Initial grid: nx={nx}, ny={ny}, nz={nz}")

    # Height
    z = compute_height(param, nz)

    # Apply filter
    z, T, rho, vz, yH = apply_height_filter(
        z, T, rho, vz, yH, Z_MIN, Z_MAX
    )

    nx, ny, nz = T.shape
    print(f"After height cut: nx={nx}, ny={ny}, nz={nz}")
    print(f"z range: {z.min():.2e} → {z.max():.2e} m")

    # Electron density
    ne = compute_electron_density(rho, yH)

    # Plot
    plot_validation(T, ne, vz, z)


# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
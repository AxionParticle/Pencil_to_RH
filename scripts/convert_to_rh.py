"""
convert_to_rh.py

Convert Pencil Code snapshot into RH-compatible HDF5 atmosphere file.

Author: Sanket Wavhal
"""

# ------------------------------------------------------------
# IMPORT LIBRARIES
# ------------------------------------------------------------
import pencil as pc
import numpy as np
import h5py


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------
DATADIR = "../data"
IVAR = 109
OUTPUT_FILE = "../output/rh_atmosphere.hdf5"

Z_MIN = -0.3e6
Z_MAX = 15e6


# ------------------------------------------------------------
# READ + CONVERT (REUSE LOGIC)
# ------------------------------------------------------------
def load_and_prepare(datadir, ivar):
    """Load Pencil data and convert to physical variables."""

    param = pc.read.param(datadir=datadir)

    var = pc.read.varraw(
        ivar=ivar,
        var_list=['uu', 'lnrho', 'lnTT', 'yH'],
        datadir=datadir,
        trimall=True
    )

    # Convert
    T   = np.exp(var.lnTT) * param.unit_temperature
    rho = np.exp(var.lnrho) * param.unit_density * 1000
    vz  = var.uz * param.unit_velocity * 1e-2
    yH  = var.yH

    # Height
    nx, ny, nz = T.shape
    z = np.linspace(param.xyz0[2], param.xyz1[2], nz)
    z = z * param.unit_length * 1e-2

    # Height filter
    mask = (z >= Z_MIN) & (z <= Z_MAX)
    z   = z[mask]
    T   = T[:, :, mask]
    rho = rho[:, :, mask]
    vz  = vz[:, :, mask]
    yH  = yH[:, :, mask]

    return param, T, rho, vz, yH, z


# ------------------------------------------------------------
# RH FORMATTING
# ------------------------------------------------------------
def convert_to_rh_format(T, rho, vz, yH, z):
    """Convert variables into RH format."""

    xH  = 1.0
    xHe = 0.081
    mp  = 1.6726219e-27

    # Mean molecular weight
    mu0 = 1 + 4 * xHe
    mu  = mu0 / (1 + yH * xH)

    # Number densities
    n_total  = rho / (mu * mp)
    nH_total = n_total
    ne       = yH * nH_total

    # Reverse height (top → observer)
    T  = T[:, :, ::-1]
    vz = vz[:, :, ::-1]
    ne = ne[:, :, ::-1]
    z  = z[::-1]

    # Hydrogen populations
    nhydr = nH_total[:, :, ::-1]
    nhydr = nhydr[np.newaxis, np.newaxis, ...]

    # Add time dimension
    T  = T[np.newaxis, ...]
    vz = vz[np.newaxis, ...]
    ne = ne[np.newaxis, ...]
    z  = z[np.newaxis, :]

    return T, vz, ne, nhydr, z


# ------------------------------------------------------------
# WRITE HDF5
# ------------------------------------------------------------
def write_hdf5(param, T, vz, ne, nhydr, z, ivar, filename):
    """Write RH atmosphere file."""

    nt, nx, ny, nz = T.shape

    with h5py.File(filename, "w") as f:

        # Coordinates
        f.create_dataset("z", data=z)

        x = np.linspace(param.xyz0[0], param.xyz1[0], nx) * param.unit_length * 1e-2
        y = np.linspace(param.xyz0[1], param.xyz1[1], ny) * param.unit_length * 1e-2

        f.create_dataset("x", data=x)
        f.create_dataset("y", data=y)

        # Main variables
        f.create_dataset("temperature", data=T)
        f.create_dataset("velocity_z", data=vz)
        f.create_dataset("electron_density", data=ne)
        f.create_dataset("hydrogen_populations", data=nhydr)

        # Metadata
        f.create_dataset("snapshot_number", data=[ivar])

        f.attrs["nt"] = nt
        f.attrs["nx"] = nx
        f.attrs["ny"] = ny
        f.attrs["nz"] = nz
        f.attrs["has_B"] = 0

    print(f"\n✅ RH file written: {filename}")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():

    print("Converting Pencil → RH...")

    param, T, rho, vz, yH, z = load_and_prepare(DATADIR, IVAR)

    T, vz, ne, nhydr, z = convert_to_rh_format(T, rho, vz, yH, z)

    write_hdf5(param, T, vz, ne, nhydr, z, IVAR, OUTPUT_FILE)


if __name__ == "__main__":
    main()
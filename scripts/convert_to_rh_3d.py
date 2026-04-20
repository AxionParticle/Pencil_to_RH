"""
convert_to_rh_3d.py

Convert Pencil Code MHD snapshot into RH 3D atmosphere (XDR format).

Features:
- Physical unit conversion
- Optional height filtering
- Optional subcube extraction
- Hydrogen populations (2-level)
- RH-compatible XDR output

Author: Sanket Wavhal
"""

# ============================================================
# IMPORTS
# ============================================================
import pencil as pc
import numpy as np
import xdrlib3 as xdrlib
import os


# ============================================================
# SETTINGS
# ============================================================

DATADIR = "../data"
IVAR = 109
OUTPUT_FILE = "../output/rh_3d.atmos"

# Toggles
USE_HEIGHT_FILTER = True
USE_SUBCUBE = True

# Height limits (m)
Z_MIN = -0.3e6
Z_MAX = 15e6

# Subcube (indices)
X_RANGE = (80, 112, 1)
Y_RANGE = (80, 112, 1)


# ============================================================
# LOAD DATA
# ============================================================
def load_data():
    """Read Pencil snapshot."""
    
    param = pc.read.param(datadir=DATADIR)

    var = pc.read.varraw(
        ivar=IVAR,
        var_list=['uu', 'lnrho', 'lnTT', 'yH'],
        datadir=DATADIR,
        trimall=True
    )

    print("✅ Data loaded")

    return param, var


# ============================================================
# CONVERT UNITS
# ============================================================
def convert_units(param, var):
    """Convert to physical units."""

    T   = np.exp(var.lnTT) * param.unit_temperature
    rho = np.exp(var.lnrho) * param.unit_density * 1000

    vx  = var.ux * param.unit_velocity * 1e-2
    vy  = var.uy * param.unit_velocity * 1e-2
    vz  = var.uz * param.unit_velocity * 1e-2

    yH  = var.yH

    return T, rho, vx, vy, vz, yH


# ============================================================
# HEIGHT GRID
# ============================================================
def compute_height(param, nz):
    z = np.linspace(param.xyz0[2], param.xyz1[2], nz)
    return z * param.unit_length * 1e-2  # m


# ============================================================
# HEIGHT FILTER
# ============================================================
def apply_height_filter(z, T, rho, vx, vy, vz, yH):
    mask = (z >= Z_MIN) & (z <= Z_MAX)

    return (
        z[mask],
        T[:, :, mask],
        rho[:, :, mask],
        vx[:, :, mask],
        vy[:, :, mask],
        vz[:, :, mask],
        yH[:, :, mask],
    )


# ============================================================
# SUBCUBE
# ============================================================
def apply_subcube(T, rho, vx, vy, vz, yH):
    xs, xe, xst = X_RANGE
    ys, ye, yst = Y_RANGE

    return (
        T[xs:xe:xst, ys:ye:yst, :],
        rho[xs:xe:xst, ys:ye:yst, :],
        vx[xs:xe:xst, ys:ye:yst, :],
        vy[xs:xe:xst, ys:ye:yst, :],
        vz[xs:xe:xst, ys:ye:yst, :],
        yH[xs:xe:xst, ys:ye:yst, :],
    )


# ============================================================
# PHYSICS
# ============================================================
def compute_densities(rho, yH):
    """Compute electron and hydrogen populations."""

    xH  = 1.0
    xHe = 0.081
    mp  = 1.6726219e-27

    mu0 = 1 + 4 * xHe
    mu  = mu0 / (1 + yH * xH)

    n_total = rho / (mu * mp)

    ne  = yH * n_total
    nH0 = n_total * (1 - yH)
    nHp = n_total * yH

    return ne, nH0, nHp


# ============================================================
# Z FLIP (RH REQUIREMENT)
# ============================================================
def flip_z(T, vx, vy, vz, ne, nH0, nHp, z):
    return (
        T[:, :, ::-1],
        vx[:, :, ::-1],
        vy[:, :, ::-1],
        vz[:, :, ::-1],
        ne[:, :, ::-1],
        nH0[:, :, ::-1],
        nHp[:, :, ::-1],
        z[::-1],
    )


# ============================================================
# WRITE XDR
# ============================================================
def write_xdr(filename, param, T, vx, vy, vz, ne, nH0, nHp, z):

    print(f"\n📝 Writing: {filename}")

    nx, ny, nz = T.shape

    # ---- unit conversion ----
    z_km  = z / 1e3
    vx_km = vx / 1e3
    vy_km = vy / 1e3
    vz_km = vz / 1e3

    dx = (param.xyz1[0] - param.xyz0[0]) * param.unit_length * 1e-2 / (nx - 1)
    dy = (param.xyz1[1] - param.xyz0[1]) * param.unit_length * 1e-2 / (ny - 1)

    dx_km = dx / 1e3
    dy_km = dy / 1e3

    vturb = np.zeros_like(T)

    NHydr = 2
    TOP = 1
    BOTTOM = 2

    p = xdrlib.Packer()

    # HEADER
    p.pack_int(nx)
    p.pack_int(ny)
    p.pack_int(nz)
    p.pack_int(NHydr)
    p.pack_int(TOP)
    p.pack_int(BOTTOM)
    p.pack_double(dx_km)
    p.pack_double(dy_km)

    for val in z_km:
        p.pack_double(float(val))

    # helper
    def pack_3d(arr):
        for v in np.ascontiguousarray(arr).ravel(order='C'):
            p.pack_double(float(v))

    # DATA
    pack_3d(T)
    pack_3d(ne)
    pack_3d(vturb)
    pack_3d(vx_km)
    pack_3d(vy_km)
    pack_3d(vz_km)
    pack_3d(nH0)
    pack_3d(nHp)

    with open(filename, "wb") as f:
        f.write(p.get_buffer())

    size = os.path.getsize(filename) / 1e6
    print(f"✅ File written ({size:.2f} MB)")


# ============================================================
# MAIN
# ============================================================
def main():

    param, var = load_data()

    T, rho, vx, vy, vz, yH = convert_units(param, var)

    nx, ny, nz = T.shape
    print(f"Initial grid: {nx} x {ny} x {nz}")

    z = compute_height(param, nz)

    if USE_HEIGHT_FILTER:
        z, T, rho, vx, vy, vz, yH = apply_height_filter(
            z, T, rho, vx, vy, vz, yH
        )
        print(f"After height filter: {T.shape}")

    if USE_SUBCUBE:
        T, rho, vx, vy, vz, yH = apply_subcube(
            T, rho, vx, vy, vz, yH
        )
        print(f"Subcube selected: {T.shape}")

    ne, nH0, nHp = compute_densities(rho, yH)

    T, vx, vy, vz, ne, nH0, nHp, z = flip_z(
        T, vx, vy, vz, ne, nH0, nHp, z
    )

    print(f"Final grid: {T.shape}")

    write_xdr(OUTPUT_FILE, param, T, vx, vy, vz, ne, nH0, nHp, z)

    print("\n🎉 READY FOR RH 3D")


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    main()
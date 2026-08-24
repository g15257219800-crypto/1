#!/usr/bin/env python3
"""Generate STEP/STL for a straight 22L (M30x2, 24° cone) x M48x2 ED stud adapter.

Drawing envelope:
  total length 70, M30 side 32, M48 stud 22, 24° internal cone, mouth Ø22.

Unspecified details follow Parker Ermeto GE-M-ED (Catalog 4300 / Part Community):
  GE22LMED  — 22L cone, nut thread M30x2, through bore D3=18, neck T1KG=27.5
  GE42LMED  — M48x2 Form E stud, hex AF=55, stud length 22
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

# --- drawing ---
L_TOTAL = 70.0
L_M30 = 32.0
L_M48 = 22.0
L_HEX = L_TOTAL - L_M30 - L_M48  # 16

CONE_MOUTH_D = 22.0
CONE_INCLUDED_DEG = 24.0
CONE_DEPTH = 10.0
INTERNAL_LAND = 15.0

# --- Parker GE-M-ED ---
HEX_AF = 55.0
BORE_D = 18.0
M30_MAJOR = 30.0
M30_PITCH = 2.0
M30_NECK_D = 27.5
M30_THREAD_LEN = 26.0
M30_CHAMFER = 1.2

M48_MAJOR = 48.0
M48_PITCH = 2.0
SEAL_COLLAR_D = 52.0
SEAL_COLLAR_H = 1.5
ED_GROOVE_D = 44.0
ED_GROOVE_W = 2.5
M48_CHAMFER = 1.5
M48_THREAD_LEN = L_M48 - SEAL_COLLAR_H - ED_GROOVE_W  # 18.0

HEX_FACE_CHAMFER = 0.6
BORE_EXIT_CHAMFER = 0.8

OUT_DIR = Path(__file__).resolve().parent
STEM = "GE22LM48X2ED"


def hex_prism(af: float, height: float) -> cq.Workplane:
    across_corners = af * 2.0 / math.sqrt(3.0)
    return cq.Workplane("XY").polygon(6, across_corners).extrude(height)


def cyl(d: float, h: float, z0: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2.0).extrude(h).translate((0, 0, z0))


def build() -> cq.Workplane:
    z_hex0 = L_M48  # 22
    z_hex1 = L_M48 + L_HEX  # 38
    z_top = L_TOTAL  # 70

    body = hex_prism(HEX_AF, L_HEX).translate((0, 0, z_hex0))
    try:
        body = body.faces(">Z or <Z").edges().chamfer(HEX_FACE_CHAMFER)
    except Exception:
        pass

    # M48 Form E stud: thread (z=0..18) + ED groove + seal collar under hex
    thread_z0 = 0.0
    groove_z0 = M48_THREAD_LEN  # 18
    collar_z0 = M48_THREAD_LEN + ED_GROOVE_W  # 20.5

    body = body.union(cyl(M48_MAJOR, M48_THREAD_LEN, thread_z0))
    body = body.union(cyl(ED_GROOVE_D, ED_GROOVE_W, groove_z0))
    body = body.union(cyl(SEAL_COLLAR_D, SEAL_COLLAR_H, collar_z0))

    # 45° start chamfer on M48 (ISO 8434)
    try:
        body = body.faces("<Z").edges("%Circle").chamfer(M48_CHAMFER)
    except Exception as exc:
        print("M48 tip chamfer skipped:", exc)

    # M30 22L end: short neck (Parker T1KG) then M30x2
    neck_h = L_M30 - M30_THREAD_LEN  # 6
    body = body.union(cyl(M30_NECK_D, neck_h, z_hex1))
    body = body.union(cyl(M30_MAJOR, M30_THREAD_LEN, z_hex1 + neck_h))
    try:
        body = body.faces(">Z").edges("%Circle").chamfer(M30_CHAMFER)
    except Exception as exc:
        print("M30 tip chamfer skipped:", exc)

    # Through bore
    body = body.cut(cyl(BORE_D, L_TOTAL + 4.0, -2.0))

    # 24° included internal cone at M30 mouth (drawing Ø22, depth 10)
    half = math.radians(CONE_INCLUDED_DEG / 2.0)
    cone_h = CONE_DEPTH
    r_face = CONE_MOUTH_D / 2.0
    r_bottom = r_face - cone_h * math.tan(half)
    if r_bottom < BORE_D / 2.0 - 0.05:
        r_bottom = BORE_D / 2.0 - 0.05
    cone = (
        cq.Workplane("XY")
        .workplane(offset=z_top - cone_h)
        .circle(max(r_bottom, 0.5))
        .workplane(offset=cone_h)
        .circle(r_face + 0.35)
        .loft(combine=True)
    )
    body = body.cut(cone)

    # Drawing 15 mm land: short relief after the cone
    relief_h = INTERNAL_LAND - CONE_DEPTH
    if relief_h > 0.3:
        body = body.cut(cyl(BORE_D + 1.2, relief_h, z_top - INTERNAL_LAND))

    try:
        body = body.faces("<Z").edges("%Circle").chamfer(BORE_EXIT_CHAMFER)
    except Exception:
        pass

    return body


def section_view(solid: cq.Workplane) -> cq.Workplane:
    """Keep +Y half so the 24° cone and ED groove are visible."""
    cutter = cq.Workplane("XZ").rect(200, 200).extrude(100)
    return solid.cut(cutter)


def export_preview_png(solid: cq.Workplane, path: Path) -> None:
    """Orthographic-ish matplotlib preview from tessellated triangles."""
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    tess = solid.val().tessellate(0.35)
    verts = np.array([[p.x, p.y, p.z] for p in tess[0]])
    faces = np.array(tess[1])
    tris = verts[faces]

    fig = plt.figure(figsize=(9.5, 7.2), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    coll = Poly3DCollection(
        tris,
        facecolor=(0.72, 0.75, 0.80, 1.0),
        edgecolor=(0.25, 0.28, 0.32, 0.18),
        linewidths=0.08,
    )
    ax.add_collection3d(coll)
    ax.auto_scale_xyz([-36, 36], [-36, 36], [0, 70])
    ax.set_box_aspect((72, 72, 70))
    ax.view_init(elev=18, azim=-55)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("GE22L × M48×2 ED  straight adapter")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def export_section_png(section: cq.Workplane, path: Path) -> None:
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    tess = section.val().tessellate(0.3)
    verts = np.array([[p.x, p.y, p.z] for p in tess[0]])
    faces = np.array(tess[1])
    tris = verts[faces]
    fig = plt.figure(figsize=(8.5, 8.5), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    coll = Poly3DCollection(
        tris,
        facecolor=(0.78, 0.82, 0.88, 1.0),
        edgecolor=(0.2, 0.22, 0.25, 0.22),
        linewidths=0.08,
    )
    ax.add_collection3d(coll)
    ax.auto_scale_xyz([-36, 36], [-4, 36], [0, 70])
    ax.set_box_aspect((72, 40, 70))
    ax.view_init(elev=2, azim=0)
    ax.set_title("Section — 24° cone (top) / ED stud (bottom)")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    solid = build()
    bb = solid.val().BoundingBox()
    print(
        f"bbox dx={bb.xlen:.3f} dy={bb.ylen:.3f} dz={bb.zlen:.3f} "
        f"z={bb.zmin:.3f}..{bb.zmax:.3f}  V={solid.val().Volume():.1f} valid={solid.val().isValid()}"
    )
    step = OUT_DIR / f"{STEM}.step"
    stl = OUT_DIR / f"{STEM}.stl"
    cq.exporters.export(solid, str(step))
    cq.exporters.export(solid, str(stl))
    print("wrote", step)
    print("wrote", stl)

    section = section_view(solid)
    cq.exporters.export(section, str(OUT_DIR / f"{STEM}_section.step"))
    cq.exporters.export(section, str(OUT_DIR / f"{STEM}_section.stl"))
    export_preview_png(solid, OUT_DIR / f"{STEM}_preview.png")
    export_section_png(section, OUT_DIR / f"{STEM}_section.png")
    print("wrote previews")


if __name__ == "__main__":
    main()

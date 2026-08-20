#!/usr/bin/env python3
"""Build envelope-accurate layout solids of Donaldson DBA5293 / P633484.

Overall L/W/H come from Donaldson product specs. Local features (square
radial-seal frame, circular 8-spoke grid with two rings and diamond
handles, panel gasket, folded handles) follow the physical parts.

Units: millimetres.
"""

from __future__ import annotations

from math import cos, radians, sin
from pathlib import Path

import cadquery as cq

OUT = Path(__file__).resolve().parent

# --- DBA5293 (primary PowerCore) -------------------------------------------
# Spec envelope: 267 x 267 x 331.5
DBA_SQUARE = 267.0
DBA_HEIGHT = 331.5
DBA_CORNER_R = 12.0
# Cylinder OD from studio photo vs square (≈0.83) and the visible plastic
# corners around the media on the square face.
DBA_CYL_D = 222.0
DBA_FRAME_H = 16.0
DBA_LIP_H = 4.0
DBA_LIP_W = 7.0
DBA_COLLAR_H = 22.0
DBA_SPOKE_W = 7.0
DBA_SPOKE_H = 7.0
DBA_HUB_D = 24.0
DBA_RIM_W = 9.0
DBA_RING_T = 6.0
# Square-face ring (one ring + corner ribs, from the earlier photo).
DBA_SQ_RING_R = 55.0
# Circular-face rings: two concentric ribs between hub and outer rim.
DBA_CIRC_RING_R = (42.0, 76.0)
DBA_DIAMOND_SIZE = 28.0
DBA_DIAMOND_WALL = 4.5
DBA_DIAMOND_H = 7.0

# --- P633484 (safety panel, from the physical part) ------------------------
# Spec envelope: 286 x 265 x 37.5
P_LEN = 286.0  # X
P_WID = 265.0  # Y
P_H = 37.5  # Z
P_CORNER_R = 8.0
P_WALL = 14.0
P_FLOOR = 3.0
P_RIB_T = 3.6
P_CHANNEL_Z = 9.0
P_CHANNEL_H = 16.0
P_CHANNEL_D = 3.2
P_SEAL_H = 5.0
P_SEAL_W = 6.0
P_PLEAT_PITCH = 4.5
P_PLEAT_H = 2.2
P_HANDLE_W = 32.0
P_HANDLE_D = 11.0


def _fillet_vertical(wp: cq.Workplane, radius: float) -> cq.Workplane:
    try:
        return wp.edges("|Z").fillet(radius)
    except Exception:
        return wp


def _union(parts: list[cq.Workplane]) -> cq.Workplane:
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


def _annulus(z: float, r_out: float, r_in: float, h: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z)
        .circle(r_out)
        .circle(r_in)
        .extrude(h)
    )


def _circular_end_grid(z: float, cyl_r: float) -> tuple[cq.Workplane, cq.Workplane]:
    """Round face from the top-down photo: rim, 8 spokes, 2 rings, 2 diamonds."""
    rim = _annulus(z, cyl_r + 0.8, cyl_r - DBA_RIM_W, DBA_SPOKE_H)
    rings = _union(
        [
            _annulus(z, r + DBA_RING_T / 2.0, r - DBA_RING_T / 2.0, DBA_SPOKE_H)
            for r in DBA_CIRC_RING_R
        ]
    )
    spokes = []
    spoke_len = cyl_r - DBA_HUB_D / 2.0 - 1.0
    for i in range(8):
        ang = i * 45.0
        spokes.append(
            cq.Workplane("XY")
            .workplane(offset=z)
            .transformed(rotate=(0, 0, ang))
            .center(DBA_HUB_D / 2.0 + spoke_len / 2.0, 0)
            .rect(spoke_len, DBA_SPOKE_W)
            .extrude(DBA_SPOKE_H)
        )
    diamonds = []
    r_d = sum(DBA_CIRC_RING_R) / 2.0
    for ang in (22.5, 202.5):
        cx = r_d * cos(radians(ang))
        cy = r_d * sin(radians(ang))
        outer = (
            cq.Workplane("XY")
            .workplane(offset=z)
            .transformed(offset=(cx, cy, 0), rotate=(0, 0, ang + 45.0))
            .rect(DBA_DIAMOND_SIZE, DBA_DIAMOND_SIZE)
            .extrude(DBA_DIAMOND_H)
        )
        inner = (
            cq.Workplane("XY")
            .workplane(offset=z - 0.2)
            .transformed(offset=(cx, cy, 0), rotate=(0, 0, ang + 45.0))
            .rect(DBA_DIAMOND_SIZE - 2 * DBA_DIAMOND_WALL, DBA_DIAMOND_SIZE - 2 * DBA_DIAMOND_WALL)
            .extrude(DBA_DIAMOND_H + 0.4)
        )
        diamonds.append(outer.cut(inner))
    black = _union([rim, rings, *spokes, *diamonds])
    hub = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .circle(DBA_HUB_D / 2.0)
        .extrude(DBA_SPOKE_H)
    )
    return black, hub


def build_dba5293() -> cq.Assembly:
    cyl_r = DBA_CYL_D / 2.0
    media_h = (
        DBA_HEIGHT
        - DBA_LIP_H
        - DBA_FRAME_H
        - DBA_COLLAR_H
        - DBA_SPOKE_H
    )
    z0 = DBA_LIP_H  # top of gasket lip / bottom of square frame

    lip_outer = (
        cq.Workplane("XY")
        .rect(DBA_SQUARE, DBA_SQUARE)
        .extrude(DBA_LIP_H)
    )
    lip_outer = _fillet_vertical(lip_outer, DBA_CORNER_R)
    lip_inner = (
        cq.Workplane("XY")
        .rect(DBA_SQUARE - 2 * DBA_LIP_W, DBA_SQUARE - 2 * DBA_LIP_W)
        .extrude(DBA_LIP_H)
    )
    lip = lip_outer.cut(lip_inner)

    frame = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .rect(DBA_SQUARE, DBA_SQUARE)
        .extrude(DBA_FRAME_H)
    )
    frame = _fillet_vertical(frame, DBA_CORNER_R)
    frame = frame.cut(
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.5)
        .circle(cyl_r)
        .extrude(DBA_FRAME_H + 1.0)
    )

    collar_outer_d = DBA_CYL_D + 16.0
    collar = (
        cq.Workplane("XY")
        .workplane(offset=z0 + DBA_FRAME_H)
        .circle(collar_outer_d / 2.0)
        .extrude(DBA_COLLAR_H)
        .faces(">Z")
        .circle(cyl_r)
        .cutThruAll()
    )

    media_z = z0 + 1.5
    media = (
        cq.Workplane("XY")
        .workplane(offset=media_z)
        .circle(cyl_r - 0.4)
        .extrude(media_h + DBA_FRAME_H + DBA_COLLAR_H - 2.0)
    )

    circ_z = z0 + DBA_FRAME_H + DBA_COLLAR_H + media_h
    circ_grid, white_hub = _circular_end_grid(circ_z, cyl_r)

    # Square-face web: 8 spokes, one ring, 4 corner ribs, centre hub.
    web_z = z0
    hub = (
        cq.Workplane("XY")
        .workplane(offset=web_z)
        .circle(DBA_HUB_D / 2.0)
        .extrude(DBA_SPOKE_H)
    )
    ring = (
        cq.Workplane("XY")
        .workplane(offset=web_z)
        .circle(DBA_SQ_RING_R + DBA_RING_T / 2.0)
        .circle(DBA_SQ_RING_R - DBA_RING_T / 2.0)
        .extrude(DBA_SPOKE_H)
    )
    spokes = None
    for i in range(8):
        ang = i * 45.0
        spoke = (
            cq.Workplane("XY")
            .workplane(offset=web_z)
            .transformed(rotate=(0, 0, ang))
            .center(cyl_r / 2.0, 0)
            .rect(cyl_r - 4.0, DBA_SPOKE_W)
            .extrude(DBA_SPOKE_H)
        )
        spokes = spoke if spokes is None else spokes.union(spoke)
    corners = None
    diag = (DBA_SQUARE / 2.0 - 8.0)
    for ang in (45.0, 135.0, 225.0, 315.0):
        rib = (
            cq.Workplane("XY")
            .workplane(offset=web_z)
            .transformed(rotate=(0, 0, ang))
            .center((cyl_r + diag) / 2.0, 0)
            .rect(diag - cyl_r + 10.0, DBA_SPOKE_W)
            .extrude(DBA_SPOKE_H)
        )
        corners = rib if corners is None else corners.union(rib)

    plastic = (
        lip.union(frame)
        .union(collar)
        .union(circ_grid)
        .union(hub)
        .union(ring)
        .union(spokes)
        .union(corners)
    )

    assy = cq.Assembly(name="DBA5293_PRIMARY")
    assy.add(plastic, name="Black_Frame", color=cq.Color(0.10, 0.10, 0.10))
    assy.add(media, name="Blue_Media", color=cq.Color(0.12, 0.45, 0.85))
    assy.add(white_hub, name="White_Hub", color=cq.Color(0.93, 0.93, 0.90))
    return assy


def _panel_grid(inner_l: float, inner_w: float) -> cq.Workplane:
    """4 horizontal bars (5 rows) and staggered verticals, from the face photo."""
    z = P_FLOOR
    h = P_H - P_FLOOR - 0.8
    t = P_RIB_T
    row_h = inner_w / 5.0
    bars = []
    for i in range(1, 5):
        y = -inner_w / 2.0 + i * row_h
        bars.append(
            cq.Workplane("XY")
            .workplane(offset=z)
            .center(0, y)
            .rect(inner_l + 0.6, t)
            .extrude(h)
        )
    # Two verticals per row; offsets match the staggered photo.
    offsets = (
        (-0.28, 0.28),
        (-0.20, 0.24),
        (-0.22, 0.22),
        (-0.24, 0.18),
        (-0.12, 0.30),
    )
    verts = []
    for i, (a, b) in enumerate(offsets):
        y = -inner_w / 2.0 + (i + 0.5) * row_h
        for frac in (a, b):
            verts.append(
                cq.Workplane("XY")
                .workplane(offset=z)
                .center(frac * inner_l, y)
                .rect(t, row_h - 1.2)
                .extrude(h)
            )
    return _union(bars + verts)


def _u_handle(x: float, y: float, open_y: float) -> cq.Workplane:
    """Molded U pull. open_y is +1 or -1, pointing the opening into the media."""
    z = P_H - 9.0
    w, d, t = P_HANDLE_W, P_HANDLE_D, 3.2
    bar = cq.Workplane("XY").workplane(offset=z).center(x, y).rect(w, t).extrude(t)
    e1 = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(x - w / 2 + t / 2, y + open_y * d / 2)
        .rect(t, d)
        .extrude(t)
    )
    e2 = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(x + w / 2 - t / 2, y + open_y * d / 2)
        .rect(t, d)
        .extrude(t)
    )
    return bar.union(e1).union(e2)


def build_p633484() -> cq.Assembly:
    inner_l = P_LEN - 2 * P_WALL
    inner_w = P_WID - 2 * P_WALL
    media_h = P_H - P_FLOOR - 6.0

    frame = cq.Workplane("XY").rect(P_LEN, P_WID).extrude(P_H)
    frame = _fillet_vertical(frame, P_CORNER_R)
    frame = frame.cut(
        cq.Workplane("XY").workplane(offset=P_FLOOR).rect(inner_l, inner_w).extrude(P_H)
    )

    # Outer-wall channel (side-profile photo).
    groove = (
        cq.Workplane("XY")
        .workplane(offset=P_CHANNEL_Z)
        .rect(P_LEN + 2.0, P_WID + 2.0)
        .extrude(P_CHANNEL_H)
        .cut(
            cq.Workplane("XY")
            .workplane(offset=P_CHANNEL_Z - 0.2)
            .rect(P_LEN - 2 * P_CHANNEL_D, P_WID - 2 * P_CHANNEL_D)
            .extrude(P_CHANNEL_H + 0.4)
        )
    )
    frame = frame.cut(groove)

    # Trapezoid latch pocket on the +Y wall.
    latch_cut = (
        cq.Workplane("XZ")
        .workplane(offset=P_WID / 2.0 - P_CHANNEL_D - 0.2)
        .center(0, P_CHANNEL_Z + P_CHANNEL_H / 2.0)
        .rect(42.0, 12.0)
        .extrude(P_CHANNEL_D + 1.5)
    )
    frame = frame.cut(latch_cut)
    latch = (
        cq.Workplane("XZ")
        .workplane(offset=P_WID / 2.0 - P_CHANNEL_D + 0.4)
        .center(0, P_CHANNEL_Z + P_CHANNEL_H / 2.0)
        .moveTo(-10.0, -4.0)
        .lineTo(10.0, -4.0)
        .lineTo(7.0, 4.0)
        .lineTo(-7.0, 4.0)
        .close()
        .extrude(2.2)
    )

    # FLOW + arrows, raised in the channel on +Y.
    markings = None
    try:
        txt = (
            cq.Workplane("XZ")
            .workplane(offset=P_WID / 2.0 - 1.3)
            .center(-8.0, P_CHANNEL_Z + P_CHANNEL_H / 2.0)
            .text("FLOW", 6.5, 0.8, font="DejaVu Sans", kind="bold")
        )
        markings = txt
    except Exception:
        markings = None
    arrows = []
    for x in (-52.0, 36.0):
        arrows.append(
            cq.Workplane("XZ")
            .workplane(offset=P_WID / 2.0 - 1.3)
            .center(x, P_CHANNEL_Z + P_CHANNEL_H / 2.0)
            .moveTo(0, 5.0)
            .lineTo(4.0, -3.5)
            .lineTo(-4.0, -3.5)
            .close()
            .extrude(0.8)
        )
    arrow_solids = _union(arrows)
    if markings is not None:
        markings = markings.union(arrow_solids)
    else:
        markings = arrow_solids

    # Channel ribs around the perimeter, skipping the latch zone.
    chan_ribs = []
    pitch = 22.0
    rib_h, rib_t = P_CHANNEL_H - 1.0, 1.4
    x = -P_LEN / 2.0 + 18.0
    while x < P_LEN / 2.0 - 16.0:
        if abs(x) > 28.0:
            for y_sign in (-1.0, 1.0):
                chan_ribs.append(
                    cq.Workplane("XY")
                    .workplane(offset=P_CHANNEL_Z + 0.5)
                    .center(x, y_sign * (P_WID / 2.0 - P_CHANNEL_D / 2.0))
                    .rect(rib_t, P_CHANNEL_D - 0.4)
                    .extrude(rib_h)
                )
        x += pitch
    y = -P_WID / 2.0 + 18.0
    while y < P_WID / 2.0 - 16.0:
        for x_sign in (-1.0, 1.0):
            chan_ribs.append(
                cq.Workplane("XY")
                .workplane(offset=P_CHANNEL_Z + 0.5)
                .center(x_sign * (P_LEN / 2.0 - P_CHANNEL_D / 2.0), y)
                .rect(P_CHANNEL_D - 0.4, rib_t)
                .extrude(rib_h)
            )
        y += pitch
    channel_ribs = _union(chan_ribs)

    # Recessed pockets on the top rim.
    pockets = []
    pw, pl, pd = 7.0, 16.0, 2.2
    for i in range(8):
        x = -P_LEN / 2.0 + 24.0 + i * ((P_LEN - 48.0) / 7.0)
        for y_sign in (-1.0, 1.0):
            pockets.append(
                cq.Workplane("XY")
                .workplane(offset=P_H - pd)
                .center(x, y_sign * (P_WID / 2.0 - P_WALL / 2.0))
                .rect(pl, pw)
                .extrude(pd + 0.2)
            )
    for i in range(7):
        y = -P_WID / 2.0 + 24.0 + i * ((P_WID - 48.0) / 6.0)
        for x_sign in (-1.0, 1.0):
            pockets.append(
                cq.Workplane("XY")
                .workplane(offset=P_H - pd)
                .center(x_sign * (P_LEN / 2.0 - P_WALL / 2.0), y)
                .rect(pw, pl)
                .extrude(pd + 0.2)
            )
    frame = frame.cut(_union(pockets))

    grid = _panel_grid(inner_l, inner_w)

    hy = inner_w / 2.0 - 1.6
    handles = _u_handle(0.0, hy, open_y=-1.0).union(_u_handle(0.0, -hy, open_y=1.0))

    # Bottom bulb seal, slightly proud on the seating face.
    gasket = (
        cq.Workplane("XY")
        .rect(P_LEN - 1.0, P_WID - 1.0)
        .extrude(P_SEAL_H)
    )
    gasket = _fillet_vertical(gasket, max(P_CORNER_R - 1.0, 1.0))
    gasket = gasket.cut(
        cq.Workplane("XY").rect(P_LEN - 2 * P_SEAL_W, P_WID - 2 * P_SEAL_W).extrude(P_SEAL_H)
    )
    try:
        gasket = gasket.edges("<Z").fillet(2.2)
    except Exception:
        pass

    media = (
        cq.Workplane("XY")
        .workplane(offset=P_FLOOR)
        .rect(inner_l - 1.0, inner_w - 1.0)
        .extrude(media_h)
    )
    n = int(inner_l / P_PLEAT_PITCH)
    x0 = -inner_l / 2.0 + P_PLEAT_PITCH
    pleat_list = []
    for i in range(max(n - 1, 1)):
        pleat_list.append(
            cq.Workplane("XY")
            .workplane(offset=P_FLOOR + media_h - 0.15)
            .center(x0 + i * P_PLEAT_PITCH, 0)
            .rect(1.3, inner_w - 3.0)
            .extrude(P_PLEAT_H)
        )
    pleats = _union(pleat_list)

    black = frame.union(grid).union(channel_ribs).union(latch).union(markings).union(handles)
    assy = cq.Assembly(name="P633484_SAFETY")
    assy.add(black, name="Black_Frame", color=cq.Color(0.08, 0.08, 0.08))
    assy.add(gasket, name="Bulb_Seal", color=cq.Color(0.04, 0.04, 0.04))
    assy.add(media, name="Media", color=cq.Color(0.96, 0.62, 0.12))
    assy.add(pleats, name="Pleats", color=cq.Color(1.0, 0.70, 0.16))
    return assy


def bbox_of(assy: cq.Assembly):
    bb = assy.toCompound().BoundingBox()
    return bb


def main() -> None:
    print("Building DBA5293 ...")
    dba = build_dba5293()
    dba_path = OUT / "DBA5293_Primary.STEP"
    dba.save(str(dba_path), exportType="STEP")
    bb = bbox_of(dba)
    print(f"  saved {dba_path.name}")
    print(f"  size mm: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}  (spec 267 x 267 x 331.5)")
    print(f"  z {bb.zmin:.2f} -> {bb.zmax:.2f}")

    print("Building P633484 ...")
    pan = build_p633484()
    pan_path = OUT / "P633484_Safety.STEP"
    pan.save(str(pan_path), exportType="STEP")
    bb = bbox_of(pan)
    print(f"  saved {pan_path.name}")
    print(f"  size mm: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}  (spec 286 x 265 x 37.5)")
    print(f"  z {bb.zmin:.2f} -> {bb.zmax:.2f}")

    kit = cq.Assembly(name="DirectFlow1200_FilterKit")
    kit.add(dba, name="DBA5293", loc=cq.Location(cq.Vector(0, 0, 0)))
    # Park the safety panel beside the primary for a single import.
    kit.add(pan, name="P633484", loc=cq.Location(cq.Vector(DBA_SQUARE / 2 + P_LEN / 2 + 40, 0, 0)))
    kit_path = OUT / "DirectFlow1200_FilterKit.STEP"
    kit.save(str(kit_path), exportType="STEP")
    print(f"  saved {kit_path.name}")


if __name__ == "__main__":
    main()

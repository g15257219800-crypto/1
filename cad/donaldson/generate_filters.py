#!/usr/bin/env python3
"""Build envelope-accurate layout solids of Donaldson DBA5293 / P633484.

Overall L/W/H come from Donaldson product specs. Local features (square
radial-seal frame, circular 8-spoke grid with two rings and diamond
handles, panel gasket, circular-pipe U handles) follow the physical parts.

Units: millimetres.
"""

from __future__ import annotations

from math import radians
from pathlib import Path

import cadquery as cq
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

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
# Two peaked pulls: hollow rectangular base + 4 cylindrical rods to the apex.
DBA_BOSS_H = 26.0
DBA_BOSS_SPAN = 36.0
DBA_BOSS_R = 80.0
DBA_BOSS_WALL = 3.6
DBA_BOSS_FRAME_H = 8.0
DBA_BOSS_ROD_SIDE = 4.2

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
# Circular-section U-pipes on the long inner edges (photo of the cream face).
P_PIPE_R = 2.0
P_PIPE_LEN = 88.0
P_PIPE_DEPTH = 22.0
P_PIPE_CORNER = 6.0
# Recess media so the pipes sit just above the pleats, still under the 37.5 envelope.
P_MEDIA_TOP = P_H - 6.8


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


def _square_bar(p0: tuple[float, float, float], p1: tuple[float, float, float], side: float) -> cq.Workplane:
    """Square-section bar from p0 to p1."""
    from math import acos, degrees

    v0 = cq.Vector(*p0)
    direction = cq.Vector(*p1) - v0
    length = direction.Length
    n = direction.normalized()
    bar = cq.Workplane("XY").rect(side, side).extrude(length)
    z_axis = cq.Vector(0, 0, 1)
    if (z_axis - n).Length > 1e-7:
        if (z_axis + n).Length < 1e-7:
            bar = bar.rotate((0, 0, 0), (1, 0, 0), 180)
        else:
            axis = z_axis.cross(n)
            angle = degrees(acos(max(-1.0, min(1.0, z_axis.dot(n)))))
            bar = bar.rotate((0, 0, 0), (axis.x, axis.y, axis.z), angle)
    return bar.translate((v0.x, v0.y, v0.z))


def _round_bar(p0: tuple[float, float, float], p1: tuple[float, float, float], radius: float) -> cq.Workplane:
    """Circular-section bar from p0 to p1."""
    from math import acos, degrees

    v0 = cq.Vector(*p0)
    direction = cq.Vector(*p1) - v0
    length = direction.Length
    n = direction.normalized()
    bar = cq.Workplane("XY").circle(radius).extrude(length)
    z_axis = cq.Vector(0, 0, 1)
    if (z_axis - n).Length > 1e-7:
        if (z_axis + n).Length < 1e-7:
            bar = bar.rotate((0, 0, 0), (1, 0, 0), 180)
        else:
            axis = z_axis.cross(n)
            angle = degrees(acos(max(-1.0, min(1.0, z_axis.dot(n)))))
            bar = bar.rotate((0, 0, 0), (axis.x, axis.y, axis.z), angle)
    return bar.translate((v0.x, v0.y, v0.z))


def _pipe_elbow_xy(
    cx: float,
    cy: float,
    z: float,
    xdir: tuple[float, float],
    bend_r: float,
    pipe_r: float,
) -> cq.Workplane:
    """90° pipe elbow in the XY plane (CCW from xdir around +Z)."""
    ax = gp_Ax2(gp_Pnt(cx, cy, z), gp_Dir(0, 0, 1), gp_Dir(xdir[0], xdir[1], 0))
    solid = cq.Solid(BRepPrimAPI_MakeTorus(ax, bend_r, pipe_r, radians(90.0)).Shape())
    return cq.Workplane("XY").newObject([solid])


def _peak_boss(cx: float, cy: float, z: float) -> cq.Workplane:
    """Hollow rectangular frame with 4 square-section spokes meeting at a peak."""
    h = DBA_BOSS_H
    span = DBA_BOSS_SPAN
    wall = DBA_BOSS_WALL
    frame_h = DBA_BOSS_FRAME_H
    outer = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(cx, cy)
        .rect(span, span)
        .extrude(frame_h)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=z - 0.2)
        .center(cx, cy)
        .rect(span - 2 * wall, span - 2 * wall)
        .extrude(frame_h + 0.4)
    )
    frame = outer.cut(inner)
    inset = wall / 2.0
    s = span / 2.0 - inset
    z1 = z + frame_h
    apex = (cx, cy, z + h)
    rods = [
        _square_bar((cx + dx, cy + dy, z1), apex, DBA_BOSS_ROD_SIDE)
        for dx, dy in ((s, s), (s, -s), (-s, s), (-s, -s))
    ]
    boss = frame.union(_union(rods))
    boss = boss.cut(
        cq.Workplane("XY")
        .workplane(offset=z + h)
        .center(cx, cy)
        .rect(span + 20.0, span + 20.0)
        .extrude(20.0)
    )
    return boss


def _circular_end_grid(z: float, cyl_r: float) -> tuple[cq.Workplane, cq.Workplane]:
    """Round face from the product photo: grid plus two 4-spoke peaked pulls."""
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
    bosses = [
        _peak_boss(DBA_BOSS_R, 0.0, z + DBA_SPOKE_H),
        _peak_boss(-DBA_BOSS_R, 0.0, z + DBA_SPOKE_H),
    ]
    black = _union([rim, rings, *spokes, *bosses])
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
        - DBA_BOSS_H
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


def _pipe_u_handle(y_bar: float, toward_center: float, z: float) -> cq.Workplane:
    """Circular-section U-pipe lying on the media face, opening toward the center.

    Long bar sits on the inner long-side wall; both legs point inward.
    """
    half = P_PIPE_LEN / 2.0
    cr = P_PIPE_CORNER
    r = P_PIPE_R
    y_open = y_bar + toward_center * P_PIPE_DEPTH
    y_arc = y_bar + toward_center * cr
    long_bar = _round_bar((-half + cr, y_bar, z), (half - cr, y_bar, z), r)
    left_leg = _round_bar((-half, y_open, z), (-half, y_arc, z), r)
    right_leg = _round_bar((half, y_open, z), (half, y_arc, z), r)
    # 90° elbows: same solid as a bent tube. X-dir is the CCW start of the quarter.
    if toward_center < 0:
        left_dir, right_dir = (0.0, 1.0), (1.0, 0.0)
    else:
        left_dir, right_dir = (-1.0, 0.0), (0.0, -1.0)
    left_e = _pipe_elbow_xy(-half + cr, y_bar + toward_center * cr, z, left_dir, cr, r)
    right_e = _pipe_elbow_xy(half - cr, y_bar + toward_center * cr, z, right_dir, cr, r)
    return long_bar.union(left_leg).union(right_leg).union(left_e).union(right_e)


def build_p633484() -> cq.Assembly:
    inner_l = P_LEN - 2 * P_WALL
    inner_w = P_WID - 2 * P_WALL
    media_z = 1.0
    media_h = P_MEDIA_TOP - media_z

    frame = cq.Workplane("XY").rect(P_LEN, P_WID).extrude(P_H)
    frame = _fillet_vertical(frame, P_CORNER_R)
    frame = frame.cut(
        cq.Workplane("XY").workplane(offset=-1.0).rect(inner_l, inner_w).extrude(P_H + 2.0)
    )

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

    markings = None
    try:
        markings = (
            cq.Workplane("XZ")
            .workplane(offset=P_WID / 2.0 - 1.3)
            .center(-8.0, P_CHANNEL_Z + P_CHANNEL_H / 2.0)
            .text("FLOW", 6.5, 0.8, font="DejaVu Sans", kind="bold")
        )
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
    markings = arrow_solids if markings is None else markings.union(arrow_solids)

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

    # Safety media: cream pleats, both faces. Not the orange open face in the DBA5293 photo.
    media = (
        cq.Workplane("XY")
        .workplane(offset=media_z)
        .rect(inner_l - 0.8, inner_w - 0.8)
        .extrude(media_h)
    )
    n = int(inner_l / 8.0)
    x0 = -inner_l / 2.0 + 8.0
    pleat_list = []
    for i in range(max(n - 1, 1)):
        x = x0 + i * 8.0
        pleat_list.append(
            cq.Workplane("XY")
            .workplane(offset=P_MEDIA_TOP)
            .center(x, 0)
            .rect(1.6, inner_w - 4.0)
            .extrude(1.1)
        )
        pleat_list.append(
            cq.Workplane("XY")
            .workplane(offset=0.0)
            .center(x, 0)
            .rect(1.6, inner_w - 4.0)
            .extrude(1.1)
        )
    pleats = _union(pleat_list)
    beads = []
    for yb in (-80.0, -27.0, 27.0, 80.0):
        beads.append(
            cq.Workplane("XY")
            .workplane(offset=P_MEDIA_TOP)
            .center(0, yb)
            .rect(inner_l - 10.0, 3.0)
            .extrude(1.1)
        )
    glue = _union(beads)

    # Two circular-pipe U handles on the long inner edges, opening toward center.
    # Long bar is anchored in the inner wall; legs hover above the recessed media.
    pipe_z = P_H - 3.5
    y_inner = inner_w / 2.0 - 0.4
    handles = _pipe_u_handle(y_inner, -1.0, pipe_z).union(
        _pipe_u_handle(-y_inner, 1.0, pipe_z)
    )

    black = frame.union(channel_ribs).union(latch).union(markings).union(handles)
    assy = cq.Assembly(name="P633484_SAFETY")
    assy.add(black, name="Black_Frame", color=cq.Color(0.08, 0.08, 0.08))
    assy.add(gasket, name="Bulb_Seal", color=cq.Color(0.04, 0.04, 0.04))
    assy.add(media, name="Media", color=cq.Color(0.90, 0.86, 0.72))
    assy.add(pleats, name="Pleats", color=cq.Color(0.93, 0.89, 0.76))
    assy.add(glue, name="Glue_Beads", color=cq.Color(0.95, 0.95, 0.93))
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

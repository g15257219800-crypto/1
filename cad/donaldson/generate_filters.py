#!/usr/bin/env python3
"""Build envelope-accurate layout solids of Donaldson DBA5293 / P633484.

Overall L/W/H come from Donaldson product specs. Local features (square
radial-seal frame, 8-spoke web, circular cap grips, panel gasket, folded
handles) follow the physical parts, not official CAD.

Units: millimetres.
"""

from __future__ import annotations

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
DBA_CAP_H = 13.0
DBA_BOSS_H = 16.0
DBA_SPOKE_W = 8.0
DBA_SPOKE_H = 7.0
DBA_HUB_D = 28.0
DBA_RING_T = 6.0
DBA_RING_R = 55.0  # centreline radius of concentric ring

# --- P633484 (safety panel) -------------------------------------------------
# Spec envelope: 286 x 265 x 37.5
P_LEN = 286.0  # X
P_WID = 265.0  # Y
P_H = 37.5  # Z
P_CORNER_R = 6.0
P_WALL = 8.0
P_GASKET_Z = 8.0
P_GASKET_H = 6.0
P_GASKET_W = 5.0
P_PLEAT_PITCH = 9.0
P_PLEAT_H = 4.0
P_WIRE_D = 3.2


def _fillet_vertical(wp: cq.Workplane, radius: float) -> cq.Workplane:
    try:
        return wp.edges("|Z").fillet(radius)
    except Exception:
        return wp


def build_dba5293() -> cq.Assembly:
    cyl_r = DBA_CYL_D / 2.0
    media_h = (
        DBA_HEIGHT
        - DBA_LIP_H
        - DBA_FRAME_H
        - DBA_COLLAR_H
        - DBA_CAP_H
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
        .extrude(media_h + DBA_FRAME_H + DBA_COLLAR_H - 3.0)
    )

    cap_z = z0 + DBA_FRAME_H + DBA_COLLAR_H + media_h
    cap = (
        cq.Workplane("XY")
        .workplane(offset=cap_z)
        .circle(cyl_r + 2.0)
        .extrude(DBA_CAP_H)
    )
    # Recessed ribbed centre on the circular cap (side-view of the real part).
    cap = cap.cut(
        cq.Workplane("XY")
        .workplane(offset=cap_z + DBA_CAP_H - 4.0)
        .circle(cyl_r - 22.0)
        .extrude(5.0)
    )
    cap_ribs = cq.Workplane("XY")
    first = True
    for ang in range(0, 180, 45):
        rib = (
            cq.Workplane("XY")
            .workplane(offset=cap_z + DBA_CAP_H - 4.0)
            .transformed(rotate=(0, 0, ang))
            .center(0, 0)
            .rect(DBA_CYL_D - 50.0, 5.0)
            .extrude(3.5)
        )
        cap_ribs = rib if first else cap_ribs.union(rib)
        first = False

    # Two hollow octagonal grips on the cap, as on the standing product photo.
    boss_z = cap_z + DBA_CAP_H
    bosses = None
    for x in (-48.0, 48.0):
        boss = (
            cq.Workplane("XY")
            .workplane(offset=boss_z)
            .center(x, 0)
            .polygon(8, 34.0)
            .extrude(DBA_BOSS_H)
        )
        boss = boss.cut(
            cq.Workplane("XY")
            .workplane(offset=boss_z + 2.0)
            .center(x, 0)
            .polygon(8, 24.0)
            .extrude(DBA_BOSS_H)
        )
        bosses = boss if bosses is None else bosses.union(boss)

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
        .circle(DBA_RING_R + DBA_RING_T / 2.0)
        .circle(DBA_RING_R - DBA_RING_T / 2.0)
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
        .union(cap)
        .union(cap_ribs)
        .union(bosses)
        .union(hub)
        .union(ring)
        .union(spokes)
        .union(corners)
    )

    assy = cq.Assembly(name="DBA5293_PRIMARY")
    assy.add(
        plastic,
        name="Black_Frame",
        color=cq.Color(0.10, 0.10, 0.10),
        loc=cq.Location(cq.Vector(0, 0, 0)),
    )
    assy.add(
        media,
        name="Blue_Media",
        color=cq.Color(0.12, 0.45, 0.85),
        loc=cq.Location(cq.Vector(0, 0, 0)),
    )
    return assy


def build_p633484() -> cq.Assembly:
    inner_l = P_LEN - 2 * P_WALL
    inner_w = P_WID - 2 * P_WALL
    floor = 3.5
    # Keep media, pleats and folded handles inside the 37.5 mm spec height.
    media_h = 24.0
    pleat_h = 3.0

    frame = (
        cq.Workplane("XY")
        .rect(P_LEN, P_WID)
        .extrude(P_H)
    )
    frame = _fillet_vertical(frame, P_CORNER_R)
    pocket = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .rect(inner_l, inner_w)
        .extrude(P_H)
    )
    frame = frame.cut(pocket)

    # Groove the outer wall, then fill it with a flush gasket.
    groove = (
        cq.Workplane("XY")
        .workplane(offset=P_GASKET_Z)
        .rect(P_LEN + 2.0, P_WID + 2.0)
        .extrude(P_GASKET_H)
        .cut(
            cq.Workplane("XY")
            .workplane(offset=P_GASKET_Z - 0.2)
            .rect(P_LEN - 2 * P_GASKET_W, P_WID - 2 * P_GASKET_W)
            .extrude(P_GASKET_H + 0.4)
        )
    )
    frame = frame.cut(groove)
    gasket = (
        cq.Workplane("XY")
        .workplane(offset=P_GASKET_Z)
        .rect(P_LEN - 0.4, P_WID - 0.4)
        .extrude(P_GASKET_H)
        .cut(
            cq.Workplane("XY")
            .workplane(offset=P_GASKET_Z - 0.2)
            .rect(P_LEN - 2 * P_GASKET_W, P_WID - 2 * P_GASKET_W)
            .extrude(P_GASKET_H + 0.4)
        )
    )

    # Inset vertical ribs so they stay inside the 286 x 265 envelope.
    ribs = None
    rib_w, rib_d, rib_h = 3.0, 1.8, P_H - 12.0
    inset = 0.9
    for x in (-P_LEN / 2.0 + inset, P_LEN / 2.0 - inset):
        for y in (-90.0, -45.0, 0.0, 45.0, 90.0):
            rib = (
                cq.Workplane("XY")
                .workplane(offset=6.0)
                .center(x, y)
                .rect(rib_d, rib_w)
                .extrude(rib_h)
            )
            ribs = rib if ribs is None else ribs.union(rib)
    for y in (-P_WID / 2.0 + inset, P_WID / 2.0 - inset):
        for x in (-100.0, -50.0, 0.0, 50.0, 100.0):
            rib = (
                cq.Workplane("XY")
                .workplane(offset=6.0)
                .center(x, y)
                .rect(rib_w, rib_d)
                .extrude(rib_h)
            )
            ribs = rib if ribs is None else ribs.union(rib)

    media = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .rect(inner_l - 0.8, inner_w - 0.8)
        .extrude(media_h)
    )
    n = int(inner_l / P_PLEAT_PITCH)
    x0 = -inner_l / 2.0 + P_PLEAT_PITCH
    pleats = None
    for i in range(max(n - 1, 1)):
        x = x0 + i * P_PLEAT_PITCH
        ridge = (
            cq.Workplane("XY")
            .workplane(offset=floor + media_h - 0.2)
            .center(x, 0)
            .rect(2.2, inner_w - 4.0)
            .extrude(pleat_h)
        )
        pleats = ridge if pleats is None else pleats.union(ridge)
    beads = None
    for y in (-80.0, -27.0, 27.0, 80.0):
        bead = (
            cq.Workplane("XY")
            .workplane(offset=floor + media_h + pleat_h - 0.4)
            .center(0, y)
            .rect(inner_l - 8.0, 3.0)
            .extrude(1.4)
        )
        beads = bead if beads is None else beads.union(bead)

    # Folded wire handles on the media, below the frame rim.
    handle_z = floor + media_h + 1.2
    handles = None
    for y in (-inner_w / 2.0 + 18.0, inner_w / 2.0 - 18.0):
        bar = (
            cq.Workplane("XY")
            .workplane(offset=handle_z)
            .center(0, y)
            .rect(92.0, P_WIRE_D)
            .extrude(P_WIRE_D)
        )
        end1 = (
            cq.Workplane("XY")
            .workplane(offset=handle_z)
            .center(46.0, y)
            .rect(P_WIRE_D, 22.0)
            .extrude(P_WIRE_D)
        )
        end2 = (
            cq.Workplane("XY")
            .workplane(offset=handle_z)
            .center(-46.0, y)
            .rect(P_WIRE_D, 22.0)
            .extrude(P_WIRE_D)
        )
        one = bar.union(end1).union(end2)
        handles = one if handles is None else handles.union(one)

    black = frame.union(ribs)
    assy = cq.Assembly(name="P633484_SAFETY")
    assy.add(black, name="Black_Frame", color=cq.Color(0.08, 0.08, 0.08))
    assy.add(gasket, name="Gasket", color=cq.Color(0.05, 0.05, 0.05))
    assy.add(media, name="Media", color=cq.Color(0.90, 0.86, 0.72))
    assy.add(pleats, name="Pleats", color=cq.Color(0.93, 0.89, 0.76))
    assy.add(beads, name="Glue_Beads", color=cq.Color(0.95, 0.95, 0.93))
    assy.add(handles, name="Handles", color=cq.Color(0.12, 0.12, 0.12))
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

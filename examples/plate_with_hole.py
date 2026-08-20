# FreeCAD macro: plate with a through hole (Part boolean example)
# Run: Macro -> Macros -> Execute, or paste into the Python console.
# This has no sketch history; change the variables and run again.

import FreeCAD as App
import Part

LENGTH = 80.0  # mm
WIDTH = 50.0
THICKNESS = 8.0
HOLE_RADIUS = 4.0
HOLE_OFFSET = 16.0

doc = App.newDocument("DemoPlate")

plate = Part.makeBox(LENGTH, WIDTH, THICKNESS)
hole = Part.makeCylinder(
    HOLE_RADIUS,
    THICKNESS + 2.0,
    App.Vector(HOLE_OFFSET, WIDTH / 2.0, -1.0),
)
solid = plate.cut(hole)

Part.show(solid, "Plate")
doc.recompute()

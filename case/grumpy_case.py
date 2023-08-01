import cadquery as cq
import cadquery.selectors as cqs
from cadquery import NearestToPointSelector, exporters as exp

# CONFIGURATION OPTIONS
useAngle = True     # if True, thifts highst col to ringfinger
showKeys = False    # if True, adds keycap models (takes longer)
showPcb = False    # if True, adds keycap models (takes longer)

# CONSTANTS
spacing = 19.05     # MX-Spacing
holeSize = 14       # Platehole size
pcbThickness = 1.6  # PCB Thickness
hsThickness = 1.85   # HS Socket Thickness below PCB
# hsSafety = 0.5      # extra space to hide HS Sockets
hsSafety = 1      # extra space to hide HS Sockets

# CASE PARAMETERS
keySafety = 0.5      # extra space between keycap and case
spaceAbovePCB = 0.25 # space between PCB and Plate.
plateHeight = 5 - spaceAbovePCB # heigth of plate
colStagger = 0.25 * spacing # stagger between cols


heightAbovePlate = 8.5 # height of case rim measured from plate
heightBelowPlate = pcbThickness+hsThickness+hsSafety # height of rim hiding pcb and Sockets

overallHeight = heightAbovePlate+heightBelowPlate+plateHeight

outerRad = 5        # radius of outer edge fillets
outerRadSmall = 1.5 # radius of other outline fillets

wallWidth  = 7.5    # Wall Width (in effect only left and right)
lWallWidth = 3    # min Wallthickness for keys outside of case body

rectOffset = 0.125*19.05-colStagger/2 # rectangular case body y offset
rectHeight = 3*spacing+2*lWallWidth+colStagger # rectangular case y height


caseWidth  = 10 *spacing + 2*wallWidth  # absolute case width
caseHeight =  3*spacing + 2*wallWidth + 3*colStagger # absolute case height

# handAngle = 14.1
handAngle = 14

centerInset = 2


def getRowPos(rowOffset=0):
    """ returns x y coordinate tuple for each right hand switch of the selected row

    :param rowOffset: row number counted from the top
    :return list of coordinate tuples
    """

    topSwitchY = caseHeight/2-wallWidth-spacing/2-rowOffset*spacing


    points =  [ 
         ( 1.5 * spacing, topSwitchY - 2 * colStagger ),
         ( 2.5 * spacing, topSwitchY - 1 * colStagger ),
         ( 3.5 * spacing, topSwitchY - 2 * colStagger ),
    ]
    if (rowOffset > 0):
        # points.append(( 4.5 * spacing, topSwitchY - 3.5 * colStagger ) )
        points.append(( 4.5 * spacing, topSwitchY - 4 * colStagger ) )

    if (rowOffset < 2):
        points.append(( 0.5 * spacing, topSwitchY - 4 * colStagger ))



    return points

def getSwitchPositions(keys=True):
    """ collects all positions for the first three rows
    """
    if keys:
        return getRowPos(0) + getRowPos(1) + getRowPos(2)
    else:
        return [( 0.25 * spacing, caseHeight/2-wallWidth-spacing/2-2*spacing - 4 * colStagger )]

## ------------------------------------------------------------------------------

insetTop = 1
insetTopOffset = -0.5
insetBottom = 0
insetBottomOffset = 1

# SKETCH FOR OUTLINE WITHOUT FILLETS
so = (
    cq.Sketch()
    .push(getSwitchPositions())
    .rect(spacing+2*lWallWidth, spacing+2*lWallWidth)
    .reset()
    .push(getSwitchPositions(False))
    .rect(spacing*1.5+2*lWallWidth,spacing+2*lWallWidth)
    .reset()
    .push([(caseWidth/4-7+5,-8)])
    .rect(caseWidth/2+10, 2*spacing+2*wallWidth+2.5+10, angle=-handAngle)
    .push([(-21.2,5)])
    .rect(40-lWallWidth, 46.9, mode='s')
    .clean()
)

# testSo = cq.Workplane("XY").placeSketch(so).extrude(5).rotateAboutCenter((0,0,1),15.9)
# show_object(testSo)

# SKETCH FOR SWITCH CUTOUTS
si = (
    cq.Sketch()
    .push(getSwitchPositions())
    .rect(spacing+keySafety, spacing+keySafety)
    .reset()
    .push(getSwitchPositions(False))
    .rect(spacing*1.5+keySafety, spacing+keySafety)
    .clean()
    .reset()
    .vertices(cqs.BoxSelector( (2, caseHeight/2, 10), (caseWidth/2+2, -caseHeight/2, -10) ))
    .fillet(1)
)



# SKETCH FOR USB Cutout
su = (cq.Sketch()
    .rect(10,5)
    .reset()
    .vertices()
    .fillet(1.5)
)
# SKETCH FOR USB Cutout
suo = (cq.Sketch()
    .rect(13,7)
    .reset()
    .vertices()
    .fillet(2.5)
)

suo_down = (cq.Sketch()
    .rect(12.5,7.5)
    .reset()
    # .vertices(">Y")
    .vertices()
    .fillet(2.5)
)


# BOTTOM
bottom = (
    cq.Workplane("XY")
    .placeSketch(so)
    .extrude(heightBelowPlate)
    .rotate((0,0,0),(0,0,1),handAngle)
    .translate((4.33,0,0))
    .edges("|Z")
    .edges(cqs.BoxSelector( (caseWidth/2, caseHeight, 0), (caseWidth, -caseHeight, overallHeight) ))
    .fillet(outerRad)
    .moveTo(-20,0)
    .rect(40,caseHeight*2)
    .cutBlind(overallHeight)
    .faces(cqs.SumSelector(cqs.StringSyntaxSelector("<Z or >Z or <X"),cqs.AndSelector(cqs.StringSyntaxSelector("#Z"),cqs.BoxSelector((0,-20,0),(20,10,overallHeight)))))
    .shell(-lWallWidth,'intersection')
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight, 0), (caseWidth/2-20, -caseHeight, overallHeight) ))
    .fillet(outerRadSmall)
)


# PLATE
plate = (
    cq.Workplane("XY", origin=(0,0,heightBelowPlate))
    .placeSketch(so)
    .extrude(plateHeight)
    .edges("|Z")
    .edges(cqs.BoxSelector( (caseWidth/2-20, caseHeight, 0), (caseWidth, -caseHeight, overallHeight) ))
    .fillet(outerRad)
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight, heightBelowPlate), (caseWidth/2-20, -caseHeight, overallHeight) ))
    .fillet(outerRadSmall)
    .edges("|Z")
    .edges(cqs.BoxSelector( (-30, -caseHeight, heightBelowPlate), (0, -40, overallHeight) ))
    .fillet(outerRadSmall)
    .edges("|Z")
    .edges(cqs.NearestToPointSelector((0,-10,heightBelowPlate+plateHeight/2)))
    .fillet(outerRadSmall)
    .faces(">Z").workplane()
    .pushPoints(getSwitchPositions())
    .rect(holeSize,holeSize)
    .cutBlind(-overallHeight)
    .pushPoints(getSwitchPositions(False))
    .rect(holeSize, holeSize)
    .cutBlind(-overallHeight)
    .faces(">Z").workplane(offset=-1.5)
    .pushPoints(getSwitchPositions())
    .rect(5,holeSize+2)
    .cutBlind(-plateHeight)
    .pushPoints(getSwitchPositions(False))
    .rect(5,holeSize+2)
    .cutBlind(-plateHeight)
    .rotate((0,0,0),(0,0,1),handAngle)
    .translate((4.33,0,0))
    .moveTo(-20,0)
    .rect(40,caseHeight*2)
    .cutBlind(-overallHeight)
)
show_object(plate)

# TOP
top = (
    cq.Workplane("XY", origin=(0,0,heightBelowPlate+plateHeight))
    .placeSketch(so)
    .extrude(heightAbovePlate)
    .faces(">Z").workplane()
    .placeSketch(si)
    .cutBlind(-heightAbovePlate)
    .faces(">Z").workplane()
    .pushPoints(getSwitchPositions())
    .rect(holeSize,holeSize)
    .cutBlind(-overallHeight)
    .rotate((0,0,0),(0,0,1),handAngle)
    .translate((4.33,0,0))
    .edges("|Z")
    .edges(cqs.BoxSelector( (caseWidth/2, caseHeight, 0), (caseWidth, -caseHeight, overallHeight) ))
    .fillet(outerRad)
    .edges("|Z")
    .edges(cqs.BoxSelector( (2, caseHeight, heightBelowPlate), (caseWidth/2, -caseHeight, overallHeight) ))
    .fillet(outerRadSmall)
    .moveTo(-20,0)
    .rect(40,caseHeight*2)
    .cutBlind(-overallHeight)
    .faces(">Z")
    .faces(cqs.NearestToPointSelector((0,-20, overallHeight))).wires().toPending()
    .cutBlind(-centerInset)
)

half = (
    bottom.union(plate.union(top))
)

full = (
    half.mirror("YZ",union=True)
    .edges("|Z")
    .edges(cqs.BoxSelector( (-1, caseHeight, heightBelowPlate+plateHeight+1), (1, -caseHeight*2, overallHeight) ))
    .fillet(1)
    .faces(cqs.NearestToPointSelector((0,-10, overallHeight))).wires().translate((0,42+0.1*lWallWidth, centerInset)).item(1).rotateAboutCenter((0,0,1), 180).toPending()
    .cutBlind(-2)
    .edges("|Z")
    .edges(cqs.NearestToPointSelector((0,-20,0)))
    .fillet(2)
    .edges("|Z")
    .edges(cqs.NearestToPointSelector((0,15,overallHeight)))
    .fillet(0.5)
    .faces("|Y")
    .edges(cqs.BoxSelector( (-20, 10, overallHeight-centerInset), (20, 120, overallHeight) ))
    .fillet(outerRadSmall)
    .faces(">Z")
    .faces(cqs.NearestToPointSelector((0,caseHeight/2, overallHeight)))
    .wires().item(0)
    .chamfer(1)
    .faces(">Z")
    .faces(cqs.NearestToPointSelector((0,caseHeight/2, overallHeight)))
    .wires().item(1)
    .chamfer(0.5)
    .faces("|Z")
    .faces(cqs.NearestToPointSelector((0,-10, overallHeight-centerInset)))
    .wires().item(0)
    .chamfer(0.5)
    .faces(cqs.NearestToPointSelector((0,-10, overallHeight-centerInset)))
    .wires().item(1)
    .chamfer(0.5 )
    .faces("<Z")
    .wires().item(1)
    .chamfer(0.7)
    .faces(cqs.NearestToPointSelector((0,caseHeight, heightBelowPlate+plateHeight/2)))
    .workplane().tag("usbPlane")
    # .move(0, 5.5)
    .move(0, heightBelowPlate)
    .placeSketch(su)
    .cutBlind(-5)
    .workplaneFromTagged("usbPlane")
    # .move(0, 5.5)
    .move(0, heightBelowPlate)
    .placeSketch(suo_down)
    .cutBlind(-1)
    # .faces(cqs.NearestToPointSelector((0,caseHeight, heightBelowPlate+plateHeight/2)))
    # .wires().item(1)
    # .chamfer(0.5)
    .faces("|Y")
    .faces(cqs.NearestToPointSelector((0,35, 5.5)))
    .wires().item(1)
    .chamfer(0.75)
)


# # exp.export(full.faces("<Z"), "/home/matthias/Data/Keyboards/CoSiNe/case/strangeBottom.dxf", exp.ExportTypes.DXF)
# # exp.export(full.faces(">Z"), "/home/matthias/Data/Keyboards/CoSiNe/case/strangeTop.dxf", exp.ExportTypes.DXF)

# # debug(full.faces("<Z"))
# # debug(full.faces(">Z"))
show_object(full)
# pcbface = full.faces("|Z").faces(cqs.NearestToPointSelector((0,0,heightBelowPlate)))
# exp.export(
#         pcbface, 
#         "/home/matthias/Data/Keyboards/Grumpy/case/pcbface.svg", 
#         opt={
#             "showAxes": False,
#             "projectionDir": (0,0,-1)
#             }
#         )
# exp.export(
#         half.mirror("YZ",union=True).faces("<Z"), 
#         "/home/matthias/Data/Keyboards/Grumpy/case/pcbface.dxf", 
#         )

# exp.export(full.faces("|Z").faces(cqs.NearestToPointSelector((0,0,heightBelowPlate))), "/home/matthias/Data/Keyboards/Grumpy/case/grumpypcb.dxf", exp.ExportTypes.DXF)
# debug(pcbface)
# debug(full.faces("<Z"))
# show_object(half.mirror("YZ", union=True))


import cadquery as cq
import cadquery.selectors as cqs
from cadquery import NearestToPointSelector, exporters as exp

# CONSTANTS
spacing = 19.05     # MX-Spacing
holeSize = 14       # Platehole size
pcbThickness = 1.6  # PCB Thickness
hsThickness = 1.85   # HS Socket Thickness below PCB
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

handAngle = 14 # degrees of rotation for each hand

centerInset = 2 #how much lower the inner cutout should be

## ------------------------------------------------------------------------------

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

    :param keys: if true returns alphakey positions, if false returns thumbkeyposition
    :return list of coordinate tuples
    """
    if keys:
        return getRowPos(0) + getRowPos(1) + getRowPos(2)
    else:
        return [( 0.25 * spacing, caseHeight/2-wallWidth-spacing/2-2*spacing - 4 * colStagger )]

def getAlphaKeyPos():
    return getSwitchPositions(True)

def getThumbKeyPos():
    return getSwitchPositions(False)

def getAllKeyPos():
    return getAlphaKeyPos() + getThumbKeyPos()

## ------------------------------------------------------------------------------

# CADQUERY EXTENSIONS

def _rotateAndClean(self, inverseCut = False):
    if inverseCut:
        cutDir = -1
    else:
        cutDir = 1

    obj = (
        self.rotate((0,0,0),(0,0,1),handAngle)
        .translate((4.33,0,0))
        .moveTo(-20,0)
        .rect(40,caseHeight*2)
        .cutBlind(cutDir * overallHeight)
    )
    return obj


def _filletOuterEdges(self):
    # fillet outmost edges
    obj = (
        self.edges("|Z")
        .edges(cqs.BoxSelector( (caseWidth/2, caseHeight, 0), (caseWidth, -caseHeight, overallHeight) ))
        .fillet(outerRad)
    )
    return obj


def _filletInnerEdges(self):
    # fillet inner edges
    obj = (
        self.edges("|Z")
        .edges(cqs.BoxSelector( (2, caseHeight, 0), (caseWidth/2-20, -caseHeight, overallHeight) ))
        .fillet(outerRadSmall)
    )
    return obj


def _caseShape(self, height, filletOuter=True, filletInner=True):
    obj = (        
        self.placeSketch(so)
        .extrude(height)
        .rotateAndClean()
    )
    if filletOuter:
        obj = obj.filletOuterEdges()
    
    if filletInner:
        # fillet inner edges
        obj = obj.filletInnerEdges()
    return obj

cq.Workplane.filletOuterEdges = _filletOuterEdges  # selects the ">X" edges and fillets them
cq.Workplane.filletInnerEdges = _filletInnerEdges  # selects all edges except ">X" and X<0 and fillets them
cq.Workplane.rotateAndClean = _rotateAndClean      # rotates and translates the object by hand spacing and angle
cq.Workplane.caseShape = _caseShape                # creates the base Case outline with given height and optional inner and outer fillet

## ------------------------------------------------------------------------------

# SKETCH FOR OUTLINE WITHOUT FILLETS
so = (
    cq.Sketch()
    # create outline shape for all keys w/ min. wall widht
    .push(getAlphaKeyPos())
    .rect(spacing+2*lWallWidth, spacing+2*lWallWidth)
    .reset()
    .push(getThumbKeyPos())
    .rect(spacing*1.5+2*lWallWidth,spacing+2*lWallWidth)
    .reset()
    # add rectangular outline to key shape
    .push([(caseWidth/4-7+5,-8)])
    .rect(caseWidth/2+10, 2*spacing+2*wallWidth+2.5+10, angle=-handAngle)
    # readd middle cutout
    .push([(-21.2,5)])
    .rect(40-lWallWidth, 46.9, mode='s')
    .clean()
)


# SKETCH FOR SWITCH CUTOUTS IN TOP PART
si = (
    cq.Sketch()
    # create shape for all keys w/ keysafety added
    .push(getAlphaKeyPos())
    .rect(spacing+keySafety, spacing+keySafety)
    .reset()
    .push(getThumbKeyPos())
    .rect(spacing*1.5+keySafety, spacing+keySafety)
    .clean()
    # fillet all edges except the leftmost, which will later be on the mirror plane
    .reset()
    .vertices(cqs.BoxSelector( (2, caseHeight/2, 10), (caseWidth/2+2, -caseHeight/2, -10) ))
    .fillet(1)
    .reset()
    .vertices(cqs.BoxSelector( (-2, 0, -1), (2, -caseHeight, 1) ))
    .fillet(1)
)

# SKETCH FOR INNER USB CUTOUT
su = (cq.Sketch()
    .rect(10,5)
    .reset()
    .vertices()
    .fillet(1.5)
)
# SKETCH FOR OUTER USB CUTOUT
suo = (cq.Sketch()
    .rect(13,7)
    .reset()
    .vertices()
    .fillet(2.5)
)

# SKETCH FOR OUTER USB CUTOUT w/ STRAIGHT BOTTOM
suo_down = (cq.Sketch()
    .push([(0,-1.5)])
    .rect(12.5,10.5)
    .reset()
    .vertices(">Y")
    .fillet(2.5)
)

## ------------------------------------------------------------------------------

# BOTTOM
bottom = (
    cq.Workplane("XY")
    .caseShape(heightBelowPlate, filletInner=False)
    # hollow out bottom, so only the rim remains
    .faces(cqs.SumSelector(cqs.StringSyntaxSelector("<Z or >Z or <X"),cqs.AndSelector(cqs.StringSyntaxSelector("#Z"),cqs.BoxSelector((0,-20,0),(20,10,overallHeight)))))
    .shell(-lWallWidth,'intersection')
    # fillet inner edges
    .filletInnerEdges()
)

# PLATE
plate = (
    cq.Workplane("XY", origin=(0,0,heightBelowPlate))
    .caseShape(plateHeight)
    ## add clip space for switches
    .faces(">Z").workplane().transformed(offset=(4.33,0,-1.5),rotate=(0,0,handAngle))
    .pushPoints(getAllKeyPos())
    .rect(5,holeSize+2)
    .cutBlind(-plateHeight)
    # add switch cutouts
    .faces(">Z").workplane().transformed(rotate=(0,0,handAngle))
    .pushPoints(getAllKeyPos())
    .rect(holeSize,holeSize)
    .cutBlind(-overallHeight)
)

# TOP
top = (
    cq.Workplane("XY", origin=(0,0,heightBelowPlate+plateHeight))
    .caseShape(heightAbovePlate)
    .faces(">Z").workplane().transformed(offset=(4.33,0,0),rotate=(0,0,handAngle))
    # remove keycutout
    .placeSketch(si)
    .cutBlind(-heightAbovePlate)
    # lower middle cutout
    .faces(">Z")
    .faces(cqs.NearestToPointSelector((0,-20, overallHeight))).wires().toPending()
    .cutBlind(-centerInset)
)

# MERGE ALL PARTS
half = (
    bottom.union(plate.union(top))
)

# CREATE FULL CASE
full = (
    half.mirror("YZ",union=True)
    # fillet on X=0
    .edges("|Z")
    .edges(cqs.BoxSelector( (-1, caseHeight, heightBelowPlate+plateHeight+1), (1, -caseHeight*2, overallHeight) ))
    .fillet(1)
    # add top groove
    .faces(cqs.NearestToPointSelector((0,-10, overallHeight))).wires().translate((0,42+0.1*lWallWidth, centerInset)).item(1).rotateAboutCenter((0,0,1), 180).toPending()
    .cutBlind(-2)
    # round bottom near thumbs
    .edges("|Z")
    .edges(cqs.NearestToPointSelector((0,-20,0)))
    .fillet(2)
    # round groove
    .edges("|Z")
    .edges(cqs.NearestToPointSelector((0,15,overallHeight)))
    .fillet(0.5)
    .faces("|Y")
    .edges(cqs.BoxSelector( (-20, 10, overallHeight-centerInset), (20, 120, overallHeight) ))
    .fillet(outerRadSmall)
    # add chamfer to outline
    .faces(">Z")
    .faces(cqs.NearestToPointSelector((0,caseHeight/2, overallHeight)))
    .wires().item(0)
    .chamfer(1)
    # add chamfer to keycutout
    .faces(">Z")
    .faces(cqs.NearestToPointSelector((0,caseHeight/2, overallHeight)))
    .wires().item(1)
    .chamfer(0.5)
    # add chamfer to middle cutout
    .faces("|Z")
    .faces(cqs.NearestToPointSelector((0,-10, overallHeight-centerInset)))
    .wires().item(0)
    .chamfer(0.5)
    .faces(cqs.NearestToPointSelector((0,-10, overallHeight-centerInset)))
    .wires().item(1)
    .chamfer(0.5 )
    # add chamfer to bottom rim
    .faces("<Z")
    .wires().item(1)
    .chamfer(0.7)
    # add usb cutout
    .faces(cqs.NearestToPointSelector((0,caseHeight, heightBelowPlate+plateHeight/2)))
    .workplane().tag("usbPlane")
    .move(0, heightBelowPlate)
    .placeSketch(su)
    .cutBlind(-5)
    .workplaneFromTagged("usbPlane")
    .move(0, heightBelowPlate)
    .placeSketch(suo_down)
    .cutBlind(-1)
    # chamfer usb cutout
    .faces("|Y")
    .faces(cqs.NearestToPointSelector((0,35, 5.5)))
    .wires().item(1)
    .chamfer(0.75)
    .faces("|Y")
    .faces(cqs.NearestToPointSelector((0,40, 5.5)))
    .edges(cqs.BoxSelector((-8,35,10),(8,45,-5)))
    .chamfer(0.75)
)

show_object(full)


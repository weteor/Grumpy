from build123d import *
from ocp_vscode import *
set_port(3939)
set_defaults(reset_camera=Camera.CENTER)

# CONSTANTS
spacing = 19.05     # MX-Spacing
holeSize = 14       # Platehole size
pcbThickness = 1.6  # PCB Thickness
hsThickness = 2.5    # HS Socket Thickness below PCB
hsSafety = 0.5    # extra space to hide HS Sockets

# CASE PARAMETERS
keySafety = 0.5      # extra space between keycap and case
spaceAbovePCB = 1.5 # space between PCB and Plate.
plateHeight = 5 - spaceAbovePCB # heigth of plate
colStagger = 0.25 * spacing # stagger between cols

plateToTopClearance = 1

heightAbovePlate = 8.25 # height of case rim measured from plate
heightBelowPlate = pcbThickness+hsThickness+hsSafety+spaceAbovePCB # height of rim hiding pcb and Sockets

overallHeight = heightAbovePlate+heightBelowPlate+plateHeight

outerRad = 5        # radius of outer edge fillets
outerRadSmall = 1 # radius of other outline fillets

wallWidth  = 7.5    # Wall Width (in effect only left and right)
lWallWidth = 3    # min Wallthickness for keys outside of case body

rectOffset = 0.125*19.05-colStagger/2 # rectangular case body y offset
rectHeight = 3*spacing+2*lWallWidth+colStagger # rectangular case y height


caseWidth  = 10 *spacing + 2*wallWidth  # absolute case width
caseHeight =  3*spacing + 2*wallWidth + 3*colStagger # absolute case height

handAngle = 14 # degrees of rotation for each hand

centerInset = 1.5 #how much lower the inner cutout should be

usbStraightExtra = 3 # extra Y length of cutout, if the inner cutout should be straight

#ScrewPositions = [ (-12.005, 9.185), (-53.723,-28.6), (-100.795,-28.6), (-102.795, 2.671)]
ScrewPositions = [ (-12.005, 26.76), (-53.723,-19.512), (-100.795,-19.512), (-102.795, 11.76)]

ScrewRadius = 1.1
ScrewHeadRadius = 2.1

HeatInsertHoleRadius = 3.2 / 2
HeatInsertMinHoleMaterialRadius = 2.85


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
        points.append(( 4.5 * spacing, topSwitchY - 3.5 * colStagger ) )
        #points.append(( 4.5 * spacing, topSwitchY - 4 * colStagger ) )

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

def getAllKeyPos(mirrored=False):
    keypos = getAlphaKeyPos() + getThumbKeyPos()
    if mirrored:
        return [(-x[0],x[1]) for x in keypos]
    else:
        return keypos

def getInnerEdges(object):
    obj = ( object.edges()
           .filter_by(Axis.Z)
           .filter_by(
               lambda v: v.center().X > 2 and v.center().X < (caseWidth/2-20))
           )
    return obj;
         

## ------------------------------------------------------------------------------

with BuildSketch() as SketchOutline:
    # outline shapes for alpha and thumbs
    with Locations(getAlphaKeyPos()):
        Rectangle(spacing+2*lWallWidth, spacing+2*lWallWidth)
    with Locations(getThumbKeyPos()):
        Rectangle(spacing*1.5+2*lWallWidth, spacing+2*lWallWidth)
    with Locations((caseWidth/4-7+5,-8)):
        Rectangle(caseWidth/2+10, 2*spacing+2*wallWidth+2.5+10, rotation=-handAngle)
    with Locations((-21.2,5)):
        Rectangle(40-lWallWidth, 46.9, mode=Mode.SUBTRACT)
    
with BuildSketch() as CaseOutline:
    with Locations((4.33,0,0)):
        add(SketchOutline.sketch, rotation=handAngle)
    with Locations((-20,0)):
        Rectangle(40,caseHeight*2, mode=Mode.SUBTRACT)
        
with BuildSketch() as CaseOutlineFilletOuter:
    add(CaseOutline.sketch)
    fillet(CaseOutlineFilletOuter.edges().sort_by(Axis.X)[-1].vertices(), outerRad)

with BuildSketch() as KeyCutout:
    with Locations(getAlphaKeyPos()):
        Rectangle(spacing+keySafety, spacing+keySafety)
    with Locations(getThumbKeyPos()):
        Rectangle(1.5*spacing+keySafety, spacing+keySafety)
    fillet(KeyCutout.vertices().sort_by(Axis.X)[4:], 1)
    fillet(KeyCutout.vertices().group_by(Axis.X)[0].sort_by(Axis.Y)[0], 1)
    fillet(KeyCutout.vertices().group_by(Axis.X)[2].sort_by(Axis.Y)[0], 1)

with BuildSketch() as bottomKeyCutout:
    Circle(2.75)
    with Locations([(5.08, 0)]):
        Circle(1.1)
    with Locations([(7.085, -2.33), (-5.842, -5.39) ]):
        Rectangle(2.6,2.94)
    with Locations([(3.25, -3.86)]):
        Rectangle(6.5, 6 )
    with Locations([(-0.065, -4.735)]):
        Rectangle(11.5, 4.25)
    with Locations([(5.08,-1.1)]):
        Rectangle(2.2,2.2)
    with Locations([(0,-2.75)]):
        Rectangle(5.5,5.5)
    fillet(bottomKeyCutout.vertices(), 0.5)
    with Locations([(-5.08, 0)]):
        Circle(1.1)

with BuildSketch() as USBCutoutInner:
    Rectangle(11.5,6.5+usbStraightExtra)
    fillet(USBCutoutInner.vertices(), 1.5)
    
with BuildSketch() as USBCutoutOuter:
    with Locations((0,-1.5)):
        Rectangle(12.5,10.5)
    fillet(USBCutoutOuter.vertices().group_by(Axis.Y)[-1], 1.5)
## ------------------------------------------------------------------------------
    
# Build Case Bottom 
with BuildPart() as Bottom:
    add(CaseOutlineFilletOuter.sketch)
    extrude(amount=heightBelowPlate+plateHeight+plateToTopClearance)
    # select faces that should not be offset = open faces
    remFaces  = Bottom.faces().sort_by(Axis.Z)[0]
    remFaces += Bottom.faces().sort_by(Axis.Z)[-1]
    remFaces += Bottom.faces().sort_by(Axis.X)[:5].sort_by(Axis.Y)[-4:]
    # create shell
    offset(amount=-2.75, openings=remFaces, kind=Kind.INTERSECTION)
    fillet(getInnerEdges(Bottom), outerRadSmall)
    
# Build  Top part
#with BuildPart(Plane(origin=(0,0,heightBelowPlate+plateHeight+plateToTopClearance))) as Top:
with BuildPart() as Top:
    add(CaseOutlineFilletOuter.sketch)
    #extrude(amount=heightAbovePlate-plateToTopClearance)
    extrude(amount=overallHeight)
    fillet(getInnerEdges(Top), outerRadSmall)
    # work plane for further operations
    #wPlane = Plane(origin=(4.33,0,heightBelowPlate+plateHeight+plateToTopClearance)).rotated((0,0,handAngle))
    wPlane = Plane(origin=(4.33,0,0)).rotated((0,0,handAngle))
    # add keycap cutout
    with BuildSketch(wPlane) :
        add(KeyCutout.sketch)
    #extrude(amount=heightAbovePlate, mode=Mode.SUBTRACT)
    extrude(amount=overallHeight, mode=Mode.SUBTRACT)
    # lower center cutout
    extrude(Top.faces().filter_by(Axis.Z).group_by(Axis.Z)[-1].sort_by(Axis.X)[0],
            amount=-centerInset, mode=Mode.SUBTRACT)
    #extrude(Top.faces().filter_by(Axis.Z).group_by(Axis.Z)[0].sort_by(Axis.X)[0],
    #        amount=plateToTopClearance+plateHeight)
    extrude(Top.faces().filter_by(Axis.Z).group_by(Axis.Z)[0].sort_by(Axis.X)[0],
            amount=-heightBelowPlate, mode=Mode.SUBTRACT)
    
with BuildPart() as FullCase:   
    #add(Bottom)
    add(Top)
    mirror(FullCase.part, about=Plane.YZ)
    
    # add fillets on mirrored edges
    fillet(FullCase.edges()
           .filter_by(Axis.Z)
           .filter_by(
               lambda v: (v.center().X < 0.05 and v.center().X > -0.05) and
                         ((v.center().Y < 0 and v.center().Y > -25) or v.center().Y > 7)), 1)
    
    # add top groove
    groove_wire = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[-2][0].outer_wire() #wires().sort_by(SortBy.LENGTH)[-1]
    groove_wire = groove_wire.rotate(Axis.Z, 180).translate((0,33,centerInset))
    extrude(Face(groove_wire), amount=-2, mode=Mode.SUBTRACT)
    
    # fillet top groove edges
    groove_fil_edges = FullCase.edges(Select.LAST).group_by(Axis.Y)[-1].sort_by(Axis.X)[1:-1]
    fillet(groove_fil_edges,  outerRadSmall)
    
    # outline Chamfer
    main_top_face = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[-1].sort_by(Axis.X)[0]
    chamfer(main_top_face.outer_wire().edges(), 0.99)
    chamfer(main_top_face.inner_wires().edges(), 0.5)
    
    inset_face = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[-2].sort_by(Axis.Y)[0]
    chamfer(inset_face.edges(), 0.5)
    
    bottom_face = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[0][0]
    chamfer(bottom_face.outer_wire().edges(), 0.7)

    edgeVertices = FullCase.solids()[0].edges().filter_by(GeomType.CIRCLE).group_by(Axis.X)[-1][0:2].vertices()
    rectHeight = (edgeVertices[2].Y-edgeVertices[1].Y) - 2*lWallWidth+keySafety
    rectWidth  = 2*edgeVertices[0].X - 2*lWallWidth+keySafety

    rect_center_y = (edgeVertices[2].Y+edgeVertices[1].Y)/2

    with BuildSketch(Plane(origin=(0,rect_center_y,0))) as bottomCutout:
        RectangleRounded(rectWidth,rectHeight,radius=outerRad-lWallWidth+keySafety/2)
        with BuildLine():
            add(FullCase.solids()[1].faces().sort_by(Axis.Z)[0].outer_wire().move(Location((0,-rect_center_y,0))))
        make_face(mode=Mode.SUBTRACT)

    extrude(amount=heightBelowPlate+plateHeight+plateToTopClearance, mode=Mode.SUBTRACT)


# Build  Plate 
with BuildPart(Plane(origin=(0,0,heightBelowPlate))) as Plate:
    add(CaseOutlineFilletOuter.sketch)
    extrude(amount=plateHeight)
    fillet(getInnerEdges(Plate), outerRadSmall)
    # work plane for further operations
    wPlane = Plane(origin=(4.33,0,heightBelowPlate)).rotated((0,0,handAngle))
    # add cutouts for switch clips
    with BuildSketch(wPlane) :
        with Locations(getAllKeyPos()):
            Rectangle(5,holeSize+2)
    extrude(amount=plateHeight-1.5, mode=Mode.SUBTRACT)
    # add switch cutout
    with BuildSketch(wPlane) :
        with Locations(getAllKeyPos()):
            Rectangle(holeSize,holeSize)
    extrude(amount=plateHeight, mode=Mode.SUBTRACT)
    mirror(Plate.part, about=Plane.YZ)

    # Build shape to remove from plate, so Plate sits freely in the case
    with BuildSketch() as RemOuter:
        with BuildLine() as Outer:
            add(FullCase.solids()[0].faces().sort_by(Axis.Z)[0].outer_wire().offset_2d(lWallWidth))
        make_face()
        with BuildLine() as Inner:
            add(FullCase.solids()[0].faces().sort_by(Axis.Z)[-1].inner_wires()[0].offset_2d(-1))
        make_face(mode=Mode.SUBTRACT)
    extrude(amount=15, mode=Mode.SUBTRACT)
    
    # add inner case part
    with BuildPart():
        add(FullCase.solids()[1])

with BuildPart() as splitFull:
    add(FullCase.solids()[0])

    # add bottom
    with BuildSketch():
        with BuildLine():
            add(splitFull.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0].outer_wire())
        make_face()
        with BuildLine():
            add(FullCase.solids()[1].faces().sort_by(Axis.Z)[0].inner_wires()[0])
        make_face(mode=Mode.SUBTRACT)
    extrude(amount=hsThickness)

    # usb cutout
    usb_face = FullCase.faces().filter_by(Axis.Y).group_by(Axis.Y)[-1].sort_by(SortBy.LENGTH)[-1]
    usb_plane = Plane(usb_face).shift_origin((usb_face.center().X,usb_face.center().Y,heightBelowPlate-spaceAbovePCB))
    with BuildSketch(usb_plane.shift_origin((usb_face.center().X,usb_face.center().Y,heightBelowPlate-spaceAbovePCB-usbStraightExtra/2))):
        add(USBCutoutInner.sketch)
    extrude(amount=-lWallWidth, mode=Mode.SUBTRACT)
    
    with BuildSketch(usb_plane):
        add(USBCutoutOuter.sketch, rotation=180)
    extrude(amount=-1, mode=Mode.SUBTRACT)
    
    inner_usb_edges = splitFull.faces(Select.LAST).filter_by(Axis.Y).sort_by(Axis.Y)[0].inner_wires().edges()
    outer_usb_edges = splitFull.edges(Select.LAST).group_by(Axis.Y)[-1].sort_by(Axis.X)[1:-1] 
    
    #chamfer(inner_usb_edges, 0.75)
    chamfer(outer_usb_edges, 0.75)

    

    split(bisect_by=Plane(splitFull.faces().sort_by(Axis.Z)[0]).offset(-(heightBelowPlate-spaceAbovePCB)), keep=Keep.BOTH)

with BuildPart() as TopHalf:
    add(splitFull.solids()[1])
    with BuildSketch(Plane(origin=(0,0,heightBelowPlate+plateHeight+plateToTopClearance))) as ScrewHolesTop:
        with Locations(ScrewPositions):
            Circle(HeatInsertMinHoleMaterialRadius)
            Circle(HeatInsertHoleRadius, mode=Mode.SUBTRACT)
        mirror(about=Plane.YZ)
    extrude(amount=-(plateHeight+spaceAbovePCB+0.25))

    with BuildSketch(Plane(origin=(0,0,heightBelowPlate-spaceAbovePCB))) as OringSub_top:
        with Locations(ScrewPositions):
            Circle(2)
        mirror(about=Plane.YZ)
    extrude(amount=1, mode=Mode.SUBTRACT)


with BuildPart() as BottomHalf:
    add(splitFull.solids()[0])

    with BuildSketch() as ScrewHolesBottom:
        with Locations(ScrewPositions):
            Circle(ScrewRadius)
        mirror(about=Plane.YZ)
    extrude(amount=5, mode=Mode.SUBTRACT)

    with BuildSketch() as ScrewHeadHolesBottom:
        with Locations(ScrewPositions):
            Circle(ScrewHeadRadius)
        mirror(about=Plane.YZ)
    extrude(amount=1, mode=Mode.SUBTRACT)

    with BuildSketch(Plane(origin=(0,0,hsThickness))) as OringSub:
        with Locations(ScrewPositions):
            Circle(2)
            Circle(1, mode=Mode.SUBTRACT)
        mirror(about=Plane.YZ)
    extrude(amount=-0.5, mode=Mode.SUBTRACT)

    rPlane = Plane(origin=(4.33,0,0)).rotated((0,0,handAngle))
    # add cutouts for switch clips
    with BuildSketch(rPlane) :
        with Locations(getAllKeyPos()):
            add(bottomKeyCutout)
    extrude(amount=hsThickness, mode=Mode.SUBTRACT)
    #fillet(BottomHalf.edges(Select.LAST).filter_by(Axis.Z),0.5)

    lPlane = Plane(origin=(-4.33,0,0)).rotated((0,0,-handAngle))
    # add cutouts for switch clips
    with BuildSketch(lPlane) :
        with Locations(getAllKeyPos(mirrored=True)):
            add(bottomKeyCutout)
    extrude(amount=hsThickness, mode=Mode.SUBTRACT)
    #fillet(BottomHalf.edges(Select.LAST).filter_by(Axis.Z),0.5)
    

show_object(Plate, name="Plate" )
show_object(TopHalf, name="Top Half" )
show_object(BottomHalf, name="Bottom Half")
TopHalf.part.export_step('grumpy_T.step')
BottomHalf.part.export_step('grumpy_B.step')
Plate.part.export_step('grumpy_P.step')

TopHalf.part.export_stl('grumpy_T.stl')
BottomHalf.part.export_stl('grumpy_B.stl')
Plate.part.export_stl('grumpy_P.stl')
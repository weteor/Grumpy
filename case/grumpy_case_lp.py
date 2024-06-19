from build123d import *
from ocp_vscode import *
set_port(3939)
set_defaults(reset_camera=Camera.CENTER)

# CONSTANTS
spacing = 19.05     # MX-Spacing
holeSize = 13.9       # Platehole size
pcbThickness = 1.6  # PCB Thickness
hsThickness = 3.3-pcbThickness   # HS Socket Thickness below PCB
hsSafety = 0.3      # extra space to hide HS Sockets

# CASE PARAMETERS
keySafety = 0.5      # extra space between keycap and case
spaceAbovePCB = 0.1 # space between PCB and Plate.
plateHeight = 2.2 - spaceAbovePCB # heigth of plate
plateClipHeight = 1.2 # switch clipping (1.2 for choc, 1.5 for MX)
colStagger = 0.25 * spacing # stagger between cols


heightAbovePlate = 8.5-6.6+3.5 # height of case rim measured from plate
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

centerInset = 1 #how much lower the inner cutout should be

usbStraightExtra = 3 # extra Y length of cutout, if the inner cutout should be straight

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
        # points.append(( 4.5 * spacing, topSwitchY - 4 * colStagger ) )

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

with BuildSketch() as USBCutoutInner:
    Rectangle(11.5,6.5+usbStraightExtra)
    fillet(USBCutoutInner.vertices(), 1.5)
    
with BuildSketch() as USBCutoutOuter:
    with Locations((0,-1.5)):
        Rectangle(12.5,10.5)
    fillet(USBCutoutOuter.vertices().group_by(Axis.Y)[-1], 1.5)
## ------------------------------------------------------------------------------

bottomPlateWire = 0

with BuildPart() as FullCase:
    
    # Build Case Bottom below Plate
    with BuildPart() as Bottom:
        add(CaseOutlineFilletOuter.sketch)
        extrude(amount=heightBelowPlate)
        # select faces that should not be offset = open faces
        remFaces  = Bottom.faces().sort_by(Axis.Z)[0]
        remFaces += Bottom.faces().sort_by(Axis.Z)[-1]
        remFaces += Bottom.faces().sort_by(Axis.X)[:5].sort_by(Axis.Y)[-4:]
        # create shell
        offset(amount=-lWallWidth, openings=remFaces, kind=Kind.INTERSECTION)
        fillet(getInnerEdges(Bottom), outerRadSmall)
    
# Build  Plate part
    with BuildPart(Plane(origin=(0,0,heightBelowPlate))) as Plate:
        add(CaseOutlineFilletOuter.sketch)
        extrude(amount=plateHeight)
        fillet(getInnerEdges(Plate), outerRadSmall)
        # work plane for further operations
        wPlane = Plane(origin=(4.33,0,heightBelowPlate)).rotated((0,0,handAngle))
        # add cutouts for switch clips
        with BuildSketch(wPlane) :
            with Locations(getAllKeyPos()):
                Rectangle(holeSize+2,holeSize)
        extrude(amount=plateHeight-plateClipHeight, mode=Mode.SUBTRACT)
        # add switch cutout
        with BuildSketch(wPlane) :
            with Locations(getAllKeyPos()):
                Rectangle(holeSize,holeSize)
        extrude(amount=plateHeight, mode=Mode.SUBTRACT)
        
    # Build  Top part
    with BuildPart(Plane(origin=(0,0,heightBelowPlate+plateHeight))) as Top:
        add(CaseOutlineFilletOuter.sketch)
        extrude(amount=heightAbovePlate)
        fillet(getInnerEdges(Top), outerRadSmall)
        # work plane for further operations
        wPlane = Plane(origin=(4.33,0,heightBelowPlate+plateHeight)).rotated((0,0,handAngle))
        # add keycap cutout
        with BuildSketch(wPlane) :
            add(KeyCutout.sketch)
        extrude(amount=heightAbovePlate, mode=Mode.SUBTRACT)
        # lower center cutout
        extrude(Top.faces().filter_by(Axis.Z).group_by(Axis.Z)[-1].sort_by(Axis.X)[0],
                amount=-centerInset, mode=Mode.SUBTRACT)
        #show_object(Bottom)
        #show_object(Plate)
        #show_object(Top)
    
    mirror(FullCase.part, about=Plane.YZ)
    
    # add fillets on mirrored edges
    fillet(FullCase.edges()
           .filter_by(Axis.Z)
           .filter_by(
               lambda v: (v.center().X < 0.05 and v.center().X > -0.05) and
                         ((v.center().Y < 0 and v.center().Y > -21) or v.center().Y > 7)), 1)
    
    # add fillets on mirrored edges
    fillet(FullCase.edges()
           .filter_by(Axis.Z)
           .group_by(Axis.Z)[-1]
           .filter_by(
               lambda v: (v.center().X < 0.05 and v.center().X > -0.05) and
                         ((v.center().Y < -21 and v.center().Y > -25) or v.center().Y > 7)), 1)
    
    # add fillets on mirrored edges
    fillet(FullCase.edges()
           .filter_by(Axis.Z)
           .group_by(Axis.Z)[0]
           .filter_by(
               lambda v: (v.center().X < 0.05 and v.center().X > -0.05) and
                         ((v.center().Y < -21 and v.center().Y > -25) or v.center().Y > 7)), 2)
    # add top groove
    groove_wire = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[-2][0].outer_wire() #wires().sort_by(SortBy.LENGTH)[-1]
    groove_wire = groove_wire.rotate(Axis.Z, 180).translate((0,33,centerInset))
    extrude(Face(groove_wire), amount=-2, mode=Mode.SUBTRACT)
    
    # fillet top groove edges
    groove_fil_edges = FullCase.edges(Select.LAST).group_by(Axis.Y)[-1].sort_by(Axis.X)[1:-1]
    fillet(groove_fil_edges, outerRadSmall)
    
    # outline Chamfer
    main_top_face = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[-1].sort_by(Axis.X)[0]
    #chamfer(main_top_face.outer_wire().edges(), 1)
    #chamfer(main_top_face.inner_wires().edges(), 0.5)
    
    inset_face = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[-2].sort_by(Axis.Y)[0]
    chamfer(inset_face.edges(), 0.5)
    
    bottom_face = FullCase.faces().filter_by(Axis.Z).group_by(Axis.Z)[0][0]
    chamfer(bottom_face.outer_wire().edges(), 0.7)

    bottomPlateWire = FullCase.faces().sort_by(Axis.Z)[0].inner_wires();
    
    # usb cutout
    usb_face = FullCase.faces().filter_by(Axis.Y).group_by(Axis.Y)[-1].sort_by(SortBy.LENGTH)[-1]
    usb_plane = Plane(usb_face).shift_origin((usb_face.center().X,usb_face.center().Y,heightBelowPlate))
    with BuildSketch(usb_plane.shift_origin((usb_face.center().X,usb_face.center().Y,heightBelowPlate-usbStraightExtra/2))):
        add(USBCutoutInner.sketch)
    extrude(amount=-11, mode=Mode.SUBTRACT)
    
    with BuildSketch(usb_plane):
        add(USBCutoutOuter.sketch, rotation=180)
    extrude(amount=-1, mode=Mode.SUBTRACT)
    
    inner_usb_edges = FullCase.faces(Select.LAST).filter_by(Axis.Y).sort_by(Axis.Y)[0].inner_wires().edges()
    outer_usb_edges = FullCase.edges(Select.LAST).group_by(Axis.Y)[-1].sort_by(Axis.X)[1:-1] 
    
    #chamfer(inner_usb_edges, 0.75)
    chamfer(outer_usb_edges, 0.75)

with BuildPart() as BottomPlate:
    with BuildSketch() as bpsk:
        with BuildLine():
            add(bottomPlateWire)
        make_face()
        offset(amount=-0.2)

    extrude(amount=hsThickness)

show(FullCase )
#show(BottomPlate )
#FullCase.part.export_stl('grumpy_lp.stl')
FullCase.part.export_step('grumpy_lp.step') 
BottomPlate.part.export_step('grumpy_lp_bottom.step') 

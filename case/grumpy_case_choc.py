# %%
from build123d import *
from ocp_vscode import *
set_port(3939)
set_defaults(reset_camera=Camera.KEEP)


# CONSTANTS
spacing_x = 18     # choc spacing
spacing_y = 17     # choc spacing
holeSize = 13.9       # Platehole size
holeFillet = 1
pcbThickness = 1.6  # PCB Thickness
hsThickness = 4.1-pcbThickness   # HS Socket Thickness below PCB
hsSafety = 0.5      # extra space to hide HS Sockets

# CASE PARAMETERS
keySafety = 0.5      # extra space between keycap and case
spaceAbovePCB = 0.1 # space between PCB and Plate.
plateHeight = 2.2 - spaceAbovePCB # heigth of plate
plateClipHeight = 1.2 # switch clipping (1.2 for choc, 1.5 for MX)
colStagger = 0.25 * spacing_y # stagger between cols

heightAbovePlate = 8.5-6.6+3.5 # height of case rim measured from plate
heightBelowPlate = pcbThickness+hsThickness+hsSafety # height of rim hiding pcb and Sockets

overallHeight = heightAbovePlate+heightBelowPlate+plateHeight

outerRad = 5        # radius of outer edge fillets
outerRadSmall = 1.35 # radius of other outline fillets

wallWidth  = 7.5    # Wall Width (in effect only left and right)
lWallWidth = 3    # min Wallthickness for keys outside of case body

rectOffset = 0.125*spacing_y-colStagger/2 # rectangular case body y offset
rectHeight = 3*spacing_y+2*lWallWidth+colStagger # rectangular case y height

caseWidth  = 10 *spacing_x + 2*wallWidth  # absolute case width
caseHeight =  3*spacing_y + 2*wallWidth + 3*colStagger # absolute case height

handAngle = 14.75 # degrees of rotation for each hand

centerInset = 1 #how much lower the inner cutout should be

usbStraightExtra = 3 # extra Y length of cutout, if the inner cutout should be straight

bottom_part_thickness = 2

part_x_offset = 4.05

def getRowPos(rowOffset=0):
    """ returns x y coordinate tuple for each right hand switch of the selected row

    :param rowOffset: row number counted from the top
    :return list of coordinate tuples
    """

    topSwitchY = caseHeight/2-wallWidth-spacing_y/2-rowOffset*spacing_y


    points =  [ 
         ( 1.5 * spacing_x, topSwitchY - 2 * colStagger ),
         ( 2.5 * spacing_x, topSwitchY - 1 * colStagger ),
         ( 3.5 * spacing_x, topSwitchY - 2 * colStagger ),
    ]
    if (rowOffset > 0):
        points.append(( 4.5 * spacing_x, topSwitchY - 3.5 * colStagger ) )
        # points.append(( 4.5 * spacing, topSwitchY - 4 * colStagger ) )

    if (rowOffset < 2):
        points.append(( 0.5 * spacing_x, topSwitchY - 4 * colStagger ))
    return points

def getSwitchPositions(keys=True):
    """ collects all positions for the first three rows

    :param keys: if true returns alphakey positions, if false returns thumbkeyposition
    :return list of coordinate tuples
    """
    if keys:
        return getRowPos(0) + getRowPos(1) + getRowPos(2)
    else:
        return [( 0.25 * spacing_x, caseHeight/2-wallWidth-spacing_y/2-2*spacing_y - 4 * colStagger )]
    
def getAlphaKeyPos():
    return getSwitchPositions(True)

def getThumbKeyPos():
    return getSwitchPositions(False)

def getAllKeyPos():
    return getAlphaKeyPos() + getThumbKeyPos()

def getAllKeyPosMir():
    switchPos = list(map(lambda pnt: (-1*pnt[0], pnt[1]), getAlphaKeyPos() + getThumbKeyPos()))
    return switchPos

def getInnerEdges(object):
    obj = ( object.edges()
           .filter_by(Axis.Z)
           .filter_by(
               lambda v: v.center().X > 2 and v.center().X < (caseWidth/2-20))
           )
    return obj;
         
# %%
## ------------------------------------------------------------------------------

with BuildSketch() as SketchOutline:
    # outline shapes for alpha and thumbs
    with Locations(getAlphaKeyPos()):
        Rectangle(spacing_x+2*lWallWidth, spacing_y+2*lWallWidth)
    with Locations(getThumbKeyPos()):
        Rectangle(spacing_x*1.5+2*lWallWidth, spacing_y+2*lWallWidth)
    with Locations((caseWidth/4-7+5,-8)):
        Rectangle(caseWidth/2+10, 2*spacing_y+2*wallWidth+2.5+10, rotation=-handAngle)
    with Locations((-21.5,7.3)):
        Rectangle(40-lWallWidth, 46.9, mode=Mode.SUBTRACT)

with BuildSketch() as CaseOutline:
    with Locations((part_x_offset,0,0)):
        add(SketchOutline.sketch, rotation=handAngle)
    with Locations((-20,0)):
        Rectangle(40,caseHeight*2, mode=Mode.SUBTRACT)

with BuildSketch() as CaseOutlineFilletOuter:
    add(CaseOutline.sketch)
    fillet(CaseOutlineFilletOuter.edges().sort_by(Axis.X)[-1].vertices(), outerRad)

with BuildSketch() as KeyCutout:
    with Locations(getAlphaKeyPos()):
        Rectangle(spacing_x+keySafety, spacing_y+keySafety)
    with Locations(getThumbKeyPos()):
        Rectangle(1.5*spacing_x+keySafety, spacing_y+keySafety)
    fillet(KeyCutout.vertices().sort_by(Axis.X)[4:], 1)
    fillet(KeyCutout.vertices().group_by(Axis.X)[0].sort_by(Axis.Y)[0], 1)
    fillet(KeyCutout.vertices().group_by(Axis.X)[2].sort_by(Axis.Y)[0], 1)

with BuildSketch() as USBCutoutInner:
    Rectangle(11.5,6.5+usbStraightExtra)
    fillet(USBCutoutInner.vertices(), 1.5)
    
with BuildSketch() as USBCutoutOuter:
    with Locations((0,-1.5)):
        Rectangle(12.5,10.5)
    fillet(USBCutoutOuter.vertices().group_by(Axis.Y)[-1], 2)

with BuildSketch() as BottomKeyCutout:
    with Locations([(-5.5,0), (5.5,0)]):
        Circle(1.25)
    with Locations((0,0)):
        Circle(2)
    with Locations([(1.3-0.5, -5-0.5,9+1)]):
        Rectangle(8.6,6.5)    
    with Locations([(-5-1.3+0.5,-3.7)]):
        Rectangle(8.6,5.5)
    with Locations((-5-1.3+1.25+2/2,-2)):
        Rectangle(7.6+2.5+2,4)

with BuildSketch(Plane.XY.rotated((0,0,180))) as BottomKeyCutoutRot:
    add(BottomKeyCutout)
# %%
## ------------------------------------------------------------------------------

bottomPlateWire = 0

with BuildPart() as CaseHalf:
    
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
        wPlane = Plane(origin=(part_x_offset,0,heightBelowPlate)).rotated((0,0,handAngle))
        # add cutouts for switch clips
        with BuildSketch(wPlane) :
            with Locations(getAllKeyPos()):
                RectangleRounded(holeSize+2,holeSize, holeFillet)
        extrude(amount=plateHeight-plateClipHeight, mode=Mode.SUBTRACT)
        # add switch cutout
        with BuildSketch(wPlane) :
            with Locations(getAllKeyPos()):
                RectangleRounded(holeSize,holeSize,holeFillet)
        extrude(amount=plateHeight, mode=Mode.SUBTRACT)
  
    # Build  Top part
    with BuildPart(Plane(origin=(0,0,heightBelowPlate+plateHeight))) as Top:
        add(CaseOutlineFilletOuter.sketch)
        extrude(amount=heightAbovePlate)
        fillet(getInnerEdges(Top), outerRadSmall)
        # work plane for further operations
        wPlane = Plane(origin=(part_x_offset,0,heightBelowPlate+plateHeight)).rotated((0,0,handAngle))
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
# %%

with BuildPart() as CaseFull:
    add(CaseHalf.part)
    mirror(CaseHalf.part, about=Plane.YZ)
    
    # add fillets on mirrored edges
    fillet(CaseFull.edges()
           .filter_by(Axis.Z)
           .filter_by(
               lambda v: (v.center().X < 0.05 and v.center().X > -0.05) and
                         ((v.center().Y < 0 and v.center().Y > -19) or v.center().Y > 7)), 1)
    
    # add fillets on mirrored edges
    fillet(CaseFull.edges()
           .filter_by(Axis.Z)
           .group_by(Axis.Z)[-1]
           .filter_by(
               lambda v: (v.center().X < 0.05 and v.center().X > -0.05) and
                         ((v.center().Y < -19 and v.center().Y > -25) or v.center().Y > 7)), 1)
    
    # add fillets on mirrored edges
    fillet(CaseFull.edges()
           .filter_by(Axis.Z)
           .group_by(Axis.Z)[0]
           .filter_by(
               lambda v: (v.center().X < 0.05 and v.center().X > -0.05) and
                         ((v.center().Y < -19 and v.center().Y > -25) or v.center().Y > 7)), 2)

    # add top groove
    groove_wire = CaseFull.faces().filter_by(Axis.Z).group_by(Axis.Z)[-2][0].outer_wire() #wires().sort_by(SortBy.LENGTH)[-1]
    groove_wire = groove_wire.rotate(Axis.Z, 180).translate((0,33,centerInset))
    extrude(Face(groove_wire), amount=-2, mode=Mode.SUBTRACT)
    
    # fillet top groove edges
    #groove_fil_edges = mainCase.edges(Select.LAST).group_by(Axis.Y)[-1].sort_by(Axis.X)[1:-1]
    groove_fil_edges = CaseFull.edges(Select.LAST).group_by(Axis.Y)[-1].filter_by(Axis.Z)
    fillet(groove_fil_edges, outerRadSmall)


    # outline Chamfer
    main_top_face = CaseFull.faces().filter_by(Axis.Z).group_by(Axis.Z)[-1].sort_by(Axis.X)[0]
    #chamfer(main_top_face.outer_wire().edges(), 1)
    #chamfer(main_top_face.inner_wires().edges(), 0.5)
    
    inset_face = CaseFull.faces().filter_by(Axis.Z).group_by(Axis.Z)[-2].sort_by(Axis.Y)[0]
    chamfer(inset_face.edges(), 0.5)

    # lower bottom ridge, added back with bottom part
    extrude(CaseFull.faces().sort_by(Axis.Z)[0], amount=-bottom_part_thickness, mode=Mode.SUBTRACT)
    
    #chamfer(bottom_face.outer_wire().edges(), 0.7)

    bottomPlateWire = CaseFull.faces().sort_by(Axis.Z)[0].inner_wires();


    # usb cutout
    usb_face = CaseFull.faces().filter_by(Axis.Y).group_by(Axis.Y)[-1].sort_by(SortBy.LENGTH)[-1]
    usb_plane = Plane(usb_face).shift_origin((usb_face.center().X,usb_face.center().Y,heightBelowPlate))
    with BuildSketch(usb_plane.shift_origin((usb_face.center().X,usb_face.center().Y,heightBelowPlate-usbStraightExtra/2-0.4))):
        add(USBCutoutInner.sketch)
    extrude(amount=-11, mode=Mode.SUBTRACT)
    
    with BuildSketch(usb_plane.shift_origin((usb_face.center().X,usb_face.center().Y,heightBelowPlate-usbStraightExtra/2+1.1))):
        add(USBCutoutOuter.sketch, rotation=180)
    extrude(amount=-1, mode=Mode.SUBTRACT)
    
    inner_usb_edges = CaseFull.faces(Select.LAST).filter_by(Axis.Y).sort_by(Axis.Y)[0].inner_wires().edges()
    outer_usb_edges = CaseFull.edges(Select.LAST).group_by(Axis.Y)[-1].sort_by(Axis.X)[1:-1] 
    
    #chamfer(inner_usb_edges, 0.75)
    chamfer(outer_usb_edges, 0.75)
    show(CaseFull)

# %%

with BuildPart() as BottomPlate:
    extrude(CaseFull.faces().sort_by(Axis.Z)[0], amount=bottom_part_thickness)
    with BuildSketch():
        make_face(bottomPlateWire[0])
    extrude(amount=bottom_part_thickness)
    with BuildSketch():
        make_face(bottomPlateWire[0].offset_2d(-0.5))
    extrude(amount=hsThickness)

    middle_hole = inset_face.outer_wire().offset_2d(-1.5)

    with BuildSketch():
        make_face(middle_hole)
    extrude(amount=5, mode=Mode.SUBTRACT)
    
    wPlane = Plane(origin=(part_x_offset,0,0)).rotated((0,0,handAngle))

    #BottomPlate.part.export_step('grumpy_lp_choc_bottom_woHoles.step') 

    with BuildSketch(wPlane) :
        with Locations(getAlphaKeyPos()):
            add(BottomKeyCutout.sketch)
    extrude(amount=max(bottom_part_thickness, hsThickness), mode=Mode.SUBTRACT)

    with BuildSketch(wPlane) :
        with Locations(getThumbKeyPos()):
            add(BottomKeyCutoutRot.sketch)
    extrude(amount=max(bottom_part_thickness, hsThickness), mode=Mode.SUBTRACT)

    wPlane = Plane(origin=(-part_x_offset,0,0)).rotated((0,0,-handAngle))

    with BuildSketch(wPlane) :
        with Locations(getAllKeyPosMir()[:-1]):
            add(BottomKeyCutout.sketch)
    extrude(amount=max(bottom_part_thickness, hsThickness), mode=Mode.SUBTRACT)
    
    with BuildSketch(wPlane) :
        with Locations(getAllKeyPosMir()[-1]):
            add(BottomKeyCutoutRot.sketch)
    extrude(amount=max(bottom_part_thickness, hsThickness), mode=Mode.SUBTRACT)
    
show (BottomPlate)
BottomPlate.part.export_step('grumpy_lp_choc_bottom.step')

# %%

show(CaseFull)
#show(BottomPlate )
#FullCase.part.export_stl('grumpy_lp_choc.stl')
#FullCase.part.export_step('grumpy_lp_choc.step')
BottomPlate.part.export_step('grumpy_lp_choc_bottom.step') 
#BottomPlate.part.export_stl('grumpy_lp_choc_bottom.stl') 

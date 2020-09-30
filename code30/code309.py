"""
Hello world template
"""
import os
import sys
import json
import math
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanElementAdapter
from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_Utility as AllplanUtil

sys.path.append(os.path.dirname(__file__))
import StdReinfShapeBuilder.ProfileReinfShapeBuilder as ProfileShapeBuilder
#import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder
import StdReinfShapeBuilder.LinearBarPlacementBuilder as LinearBarBuilder

#from StdReinfShapeBuilder.ConcreteCoverProperties import ConcreteCoverProperties
from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties
#from StdReinfShapeBuilder.RotationAngles import RotationAngles

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart


# Print some information
print('Load HelloWorld.py1222')
# comt với python thì sử dụng #, hàm này được in ra ở vị trí 

# Method for checking the supported versions
def check_allplan_version(build_ele, version):
    """
    Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Delete unused arguments
    del build_ele
    del version
    #print(build_ele)
    #print(version)

    # Support all versions
    return True


# Method for element creation
def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document

    Returns:
            tuple  with created elements, handles and (otional) reinforcement.
    """
    # Delete unused arguments
    del doc
    return ([], None, None)
def create_interactor(coord_input, pyp_path, str_table_service):
    return closedstirrup(coord_input, pyp_path, str_table_service)
class closedstirrup():
    def __init__(self, coord_input, pyp_path, str_table_service):
        #input parameters
        self.coord_input        = coord_input #okie
        self.doc                = self.coord_input.GetInputViewDocument()
        self.pyp_path           = pyp_path #okie
        self.str_table_service  = str_table_service
        # self.model_ele_list     = None
        self.build_ele_service  = BuildingElementService() #okie
        self.palette_service    = None
        self.preview            = False
        #default parameters
        self.section_point      = False
        self.sel_column         = None
        self.sel_point          = None
        self.second_esc         = False
        #----------------- format parameter values
        self.com_prop = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()
        self.texturedef = None
        ##
        self.distance              = None
        self.model_ele_list        = []
        self.handle_list           = []
        ##
        self.current_pos        = AllplanReinf.ReinforcementUtil.GetNextBarPositionNumber(self.doc)
        #filter for columns
        type_query = AllplanIFW.QueryTypeID(AllplanElementAdapter.Cylinder3D_TypeUUID )
        sel_query = AllplanIFW.SelectionQuery(type_query)
        self.element_filter = AllplanIFW.ElementSelectFilterSetting(sel_query, True)
        self.ShowPalatte("ColumnReinforcement.pal")
        # try:
        #     self.read_values(self.build_ele)
        # except Exception as e:
        #     print("read value failed: ", e)

    def getdata(self):
        data = {}
        return data   
    
    def on_mouse_leave(self):
        pass
    
    def on_preview_draw(self):
        pass
    
    def modify_element_property(self, page, name, value):
        update_palette = self.palette_service.modify_element_property(page, name, value)
        # Update palette
        if update_palette:
            self.palette_service.update_palette(-1, False)
    
    def process_mouse_msg(self, mouse_msg, pnt, msg_info): #hàm chọn chuột, xem con chuột có được chọn hay không
         # Section Point
        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, True, True, self.element_filter)
        if self.coord_input.IsMouseMove(mouse_msg):
            return True
        geo_ele = self.coord_input.GetSelectedElement()
        geo_listpoint = geo_ele.GetGeometry().GetVertices()[1]
        self.x0 = geo_listpoint[0].Values()[0]
        self.y0 = geo_listpoint[0].Values()[1]
        self.z0 = geo_listpoint[0].Values()[2]
        self.x1 = geo_listpoint[1].Values()[0]
        self.y1 = geo_listpoint[1].Values()[1]
        self.z1 = geo_listpoint[1].Values()[2]
        # AllplanUtil.ShowMessageBox(str(self.x0), AllplanUtil.MB_OK)
        try:
            self.read_values(self.build_ele)
        except Exception as e:
            print("read value failed: ", e)
        # AllplanUtil.ShowMessageBox(str(self.radius) + "\n"+str(self.placement_length), AllplanUtil.MB_OK)
        reins = self.create_reinforcement();
        AllplanBaseElements.CreateElements(self.doc, AllplanGeo.Matrix3D(), reins, [], None)
        # AllplanBaseElements.CreateElements(self.doc, AllplanGeo.Matrix3D(), reins, [], None)
        # self.create_geometry()
        AllplanUtil.ShowMessageBox("okie done ", AllplanUtil.MB_OK)
        return True

    def ShowPalatte(self, palette_name):
        """ show the palatte """
        result, self.build_ele_script, self.build_ele_list, self.control_props_list,    \
            self.build_ele_composite, part_name, self.file_name = \
            self.build_ele_service.read_data_from_pyp(self.pyp_path + "\\" + palette_name,
                                                      self.str_table_service.str_table, False, 
                                                      self.str_table_service.material_str_table)

        if not result:
            return True

        self.palette_service = BuildingElementPaletteService(self.build_ele_list, self.build_ele_composite,
                                                             self.build_ele_script,
                                                             self.control_props_list, self.file_name)

        self.palette_service.show_palette(part_name)
        self.build_ele = self.build_ele_list[0]
    def read_values(self, build_ele):
        """
        Read palette parameter values

        Args:
            build_ele:  the building element.
        """
        #----------------- Extract palette geoemetry parameter values
        self.radius                     = build_ele.Radius.value
        self.placement_length           = build_ele.PlacementLength.value

        #----------------- Extract reinforcement parameter values
        self.horizontal_placement       = build_ele.HorizontalPlacement.value
        self.concrete_grade             = build_ele.ConcreteGrade.value
        self.concrete_cover             = build_ele.ConcreteCover.value
        self.diameter                   = build_ele.Diameter.value
        self.bending_roller             = build_ele.BendingRoller.value
        self.steel_grade                = build_ele.SteelGrade.value
        self.distance                   = build_ele.Distance.value
        self.stirrup_type               = build_ele.StirrupType.value

        #----------------- Extract palette format parameter values
        self.texturedef                 = AllplanBasisElements.TextureDefinition(build_ele.Surface.value)
        self.com_prop.Color             = build_ele.Color.value
        self.com_prop.Pen               = build_ele.Pen.value
        self.com_prop.Stroke            = build_ele.Stroke.value
        self.com_prop.Layer             = build_ele.Layer.value
        self.com_prop.HelpConstruction  = build_ele.UseConstructionLineMode.value
        # AllplanUtil.ShowMessageBox(str(self.radius), AllplanUtil.MB_OK)
        # print(self.placement_length)
    def on_cancel_function(self):
            #exit
        if self.second_esc:
            self.palette_service.close_palette()
            return True
        elif self.sel_column == None:
            self.palette_service.close_palette()
            return True
        elif not self.build_ele.Create_Section.value:
            self.palette_service.close_palette()
            return True
        else:
            self.CreateSection()
            self.second_esc = True
    def create_profile(self):
        """
        Create the profile of sweep solid
        Returns: created profile polyline
        """
        # define Arc path in XY plane
        arc = AllplanGeo.Arc2D(
            AllplanGeo.Point2D (self.x0,self.y0), # center
            self.radius,           # minor
            self.radius,           # major bán kính của đường tròn
            0,                     # rotation angle
            0,                     # start angle
            2 * math.pi,           # delta angle
            True)                  # counterclockwise
        path = AllplanGeo.Path2D()
        path += arc

        circumference = 2 * math.pi * self.radius

        division = AllplanGeo.DivisionPoints(path, circumference / 36., 0.)

        points = division.GetPoints()

        profile = AllplanGeo.Polyline3D()
        profile += AllplanGeo.Point3D (arc.GetStartPoint().X, arc.GetStartPoint().Y, 0.0)
        for point in points:
            profile += AllplanGeo.Point3D (point.X, point.Y, 0.0)
        return profile
    def create_reinforcement(self):
        """
        Create the stirrup placement
        Returns: created stirrup reinforcement
        """
        diameter = self.diameter
        bending_roller = self.bending_roller
        steel_grade = self.steel_grade
        concrete_grade = self.concrete_grade
        concrete_cover = self.concrete_cover
        distance = self.distance
        z1 = self.z1
        x1 = self.x1
        y1 = self.y1
        z0 = self.z0
        x0 = self.x0
        y0 = self.y0
        dd = z1 - z0
        radius = self.radius
        # get the profile
        profile = self.create_profile()
        print(profile)
        # define shape properties
        shape_props = ReinforcementShapeProperties.rebar(diameter,bending_roller, steel_grade,
                                                         concrete_grade, AllplanReinf.BendingShapeType.Freeform)

        placement_start_point = AllplanGeo.Point3D(-radius,0, 0)
        placement_end_point = AllplanGeo.Point3D(-radius, 0, dd)
        rotation_matrix = AllplanGeo.Matrix3D()
        rot_angle = AllplanGeo.Angle()
        rot_angle.SetDeg(360)
        rotation_matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(x0, y0, z0), AllplanGeo.Point3D(x1, y1, z1)), rot_angle)
        # define shape
        shape = ProfileShapeBuilder.create_profile_stirrup(profile,
                                                           rotation_matrix,
                                                           shape_props,
                                                           concrete_cover,
                                                           AllplanReinf.StirrupType.FullCircle)

        reinforcement = [1]
        # if shape.IsValid():
        reinforcement.append (LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(
                1, shape,
                placement_start_point, placement_end_point,
                concrete_cover, concrete_cover,distance))
        reinforcement.remove(reinforcement[0])
        return reinforcement
    def create_geometry(self):
        """
        Create the geometry
        Returns: created poylhedron
        """
        # Define cylinder placement axis for horizontal / vertical placement
        z1 = self.z1
        x1 = self.x1
        y1 = self.y1
        z0 = self.z0
        x0 = self.x0
        y0 = self.y0
        radius = self.radius
        a = z1 - z0
        b = x0 - radius
        # AllplanUtil.ShowMessageBox(str(self.x-self.radius), AllplanUtil.MB_OK)
        AllplanUtil.ShowMessageBox(str(b), AllplanUtil.MB_OK)
        cylinder = AllplanGeo.Cylinder3D(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(b, self.y0, self.z0),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            self.radius, self.radius,
            AllplanGeo.Point3D(0, 0, a))
        com_prop1 = AllplanBaseElements.CommonProperties()
        com_prop1.GetGlobalProperties()
        model_elem_list1 = [AllplanBasisElements.ModelElement3D(com_prop1, cylinder)]
        AllplanBaseElements.CreateElements(self.doc, AllplanGeo.Matrix3D(), model_elem_list1, [], None)
        # return cylinder
    

"""
Example Script for Closed Stirrup Full Circle
"""
import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements

import StdReinfShapeBuilder.ProfileReinfShapeBuilder as ProfileShapeBuilder
#import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder
import StdReinfShapeBuilder.LinearBarPlacementBuilder as LinearBarBuilder

#from StdReinfShapeBuilder.ConcreteCoverProperties import ConcreteCoverProperties
from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties
#from StdReinfShapeBuilder.RotationAngles import RotationAngles

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart

print('Loading script: ClosedStirrup_FullCircle.py')


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

    # Support all versions
    return True

def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """

    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)

def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    element = ClosedStirrup(doc)
    return element.create(build_ele)


class ClosedStirrup():
    """
    Definition of class ClosedStirrup
    """

    def __init__(self, doc):
        """
        Initialisation of class ClosedStirrup

        Args:
            doc: input document
        """

        self.model_ele_list        = []
        self.handle_list           = []
        self.document              = doc

        #----------------- geoemetry parameter values
        self.radius                = 10000
        self.placement_length      = 3000

        #----------------- reinforcement parameter values
        self.horizontal_placement  = None
        self.concrete_grade        = None
        self.concrete_cover        = None
        self.diameter              = None
        self.bending_roller        = None
        self.steel_grade           = None
        self.distance              = None
        self.mesh_type             = None
        self.stirrup_type          = None

        #----------------- format parameter values
        self.com_prop = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()
        self.texturedef = None

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

    def create(self, build_ele):
        """
        Create the elements

        Args:
            build_ele:  the building element.

        Returns:
            tuple  with created elements and handles.
        """
        self.read_values(build_ele)
        self.create_stirrup(build_ele)
        self.create_handles()
        return (self.model_ele_list, self.handle_list)

    def create_stirrup(self, build_ele):
        """
        Create the geometry

        Args:
            build_ele:  the building element.
        """
        polyhedron = self.create_geometry()
        reinforcement = self.create_reinforcement()

        # for visualisation get the profile
        profile = self.create_profile()


        #----------------- Create PythonPart view
        views = [View2D3D ([AllplanBasisElements.ModelElement3D(self.com_prop, self.texturedef, polyhedron),
                            AllplanBasisElements.ModelElement3D(self.com_prop, profile)])]

        #----------------- Create PythonPart
        pythonpart = PythonPart ("Stirrup",
                                 parameter_list = build_ele.get_params_list(),
                                 hash_value     = build_ele.get_hash(),
                                 python_file    = build_ele.pyp_file_name,
                                 views          = views,
                                 reinforcement  = reinforcement,
                                 common_props   = self.com_prop)

        self.model_ele_list = pythonpart.create()

    def create_geometry(self):
        """
        Create the geometry
        Returns: created poylhedron
        """
        # Define cylinder placement axis for horizontal / vertical placement
        xaxis = AllplanGeo.Vector3D(1, 0, 0)
        zaxis = AllplanGeo.Vector3D(0, 1, 0)
        if not self.horizontal_placement:
            xaxis = AllplanGeo.Vector3D(1, 0, 0)
            zaxis = AllplanGeo.Vector3D(0, 0, 1)

        apex = AllplanGeo.Point3D(0, 0, self.placement_length)

        cylinder = AllplanGeo.Cylinder3D(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(), xaxis, zaxis), self.radius, self.radius, apex) #okie, tạo cylinder thì đơn giản thôi, không có gì khó cả

        return cylinder

    def create_profile(self):
        """
        Create the profile of sweep solid
        Returns: created profile polyline
        """

        # define Arc path in XY plane
        arc = AllplanGeo.Arc2D(
            AllplanGeo.Point2D (), # center
            self.radius,           # minor
            self.radius,           # major
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

        rotation_matrix = AllplanGeo.Matrix3D()
        rot_angle = AllplanGeo.Angle()
        rot_angle.SetDeg(90)
        rotation_matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(-1000, 0, 0), AllplanGeo.Point3D(1000, 0, 0)), rot_angle)
        profile = AllplanGeo.Transform (profile, rotation_matrix)

        return profile

    def create_reinforcement(self):
        """
        Create the stirrup placement
        Returns: created stirrup reinforcement
        """
        # get the profile
        profile = self.create_profile()

        # define shape properties
        shape_props = ReinforcementShapeProperties.rebar(self.diameter, self.bending_roller, self.steel_grade,
                                                         self.concrete_grade, AllplanReinf.BendingShapeType.Freeform)

        placement_start_point = AllplanGeo.Point3D(0, 0, 0)
        placement_end_point = AllplanGeo.Point3D(0, self.placement_length, 0)
        rotation_matrix = ProfileShapeBuilder.get_rotation_matrix_from_xz_to_xy()
        if not self.horizontal_placement:
            rotation_matrix = AllplanGeo.Matrix3D()
            placement_end_point = AllplanGeo.Point3D(0, 0, self.placement_length)

        # define shape
        shape = ProfileShapeBuilder.create_profile_stirrup(profile,
                                                           rotation_matrix,
                                                           shape_props,
                                                           self.concrete_cover,
                                                           AllplanReinf.StirrupType.FullCircle)

        reinforcement = []
        if shape.IsValid():
            reinforcement.append (LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(
                1, shape,
                placement_start_point, placement_end_point,
                self.concrete_cover, self.concrete_cover, self.distance))
        return reinforcement

    def create_handles(self):
        """
        Create handles

        Args:
            build_ele:  the building element.
        """
        # Handle for Radius
        self.handle_list.append(
            HandleProperties("Radius",
                             AllplanGeo.Point3D(self.radius, 0, 0),
                             AllplanGeo.Point3D(0, 0, 0),
                             [("Radius", HandleDirection.x_dir)],
                             HandleDirection.x_dir))

        # Handle for Placement length
        if self.horizontal_placement:
            self.handle_list.append(
                HandleProperties("PlacementLength",
                                 AllplanGeo.Point3D(0, self.placement_length, 0),
                                 AllplanGeo.Point3D(0, 0, 0),
                                 [("PlacementLength", HandleDirection.y_dir)],
                                 HandleDirection.y_dir,
                                 True))
        else:
            self.handle_list.append(
                HandleProperties("PlacementLength",
                                 AllplanGeo.Point3D(0, 0, self.placement_length),
                                 AllplanGeo.Point3D(0, 0, 0),
                                 [("PlacementLength", HandleDirection.z_dir)],
                                 HandleDirection.z_dir,
                                 True))




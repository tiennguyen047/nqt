import NemAll_Python_Reinforcement as AllplanReinf

import StdReinfShapeBuilder.LinearBarPlacementBuilder as LinearBarBuilder
import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder

from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties

import ColumnPoints as Points
import ColumnShape as Shape

import math

class General_params():
    # Genereal parameters
    def __init__(self, point_list, rebar_prop):
        self.rebar_prop = rebar_prop
        self.length     = abs(point_list[1].GetDistance(point_list[0]))
        self.width      = abs(point_list[3].GetDistance(point_list[0]))
        self.height     = abs(point_list[0].GetDistance(point_list[4]))
        self.angle      = Points.get2dangle_fr_3d(point_list[0], point_list[1])

class Rebar_prop():
    # Rebar properties
    def __init__(self, bending_roller, steel_grade, concr_grade):
        self.bending_roller = bending_roller
        self.steel_grade    = steel_grade
        self.concr_grade    = concr_grade

class Rebar_hook():
    # Rebar hooks
    def __init__(self, start_hook, end_hook, start_angle, end_angle):
        self.start_hook  = start_hook
        self.end_hook    = end_hook
        self.start_angle = start_angle
        self.end_angle   = end_angle

def round_up(number, round):
    # Round up to round mm (example 50 mm)
    if number%round != 0:
        return (number-number%round) + round
    else:
        return number

def round_down(number, round): 
# Round dơn to round mm (example 50 mm)
    if number%round != 0:
        return (number-number%round)
    else:
        return number

# Get distance for sub rebars in beam
def dist_for_subrebar(beam_width, main_diameter, sub_diameter, stir_diameter,
                     concr_cover, main_number, sub_number):
    # Distance from maindiameter to subdiameter (Tính từ tâm thép)
    axis_distance = (beam_width - 2*concr_cover - 2*stir_diameter - main_diameter)\
                    /(main_number + sub_number - 1)
    # Distance from maindiameter to subdiameter (Tính từ mép thép)
    distance = axis_distance - (main_diameter + sub_diameter)/2
    # Distance from beam to subdiameter (Tính từ mép dầm đến mép thép phụ)
    return concr_cover + main_diameter + stir_diameter + distance


# Longit using counting
def LongitCount(rebar_prop, rebar_hook, diameter, length, rot_angle, concr_prop, 
                point1, point2, concr_bottom, concr_top, number, mark_no=2):

    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = GeneralShapeBuilder.create_longitudinal_shape_with_user_hooks(
                                    length, rot_angle, shape_props, concr_prop, 
                                    rebar_hook.start_hook, rebar_hook.end_hook, 
                                    rebar_hook.start_angle, rebar_hook.end_angle)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(
                                    mark_no, bendingshape, point1, point2,
                                    concr_bottom, concr_top, number)
    return rebars

# Longit using counting
def LongitSpacing(rebar_prop, rebar_hook, diameter, length, rot_angle, concr_prop, 
                point1, point2, concr_bottom, concr_top, spacing, mark_no=2):

    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = GeneralShapeBuilder.create_longitudinal_shape_with_user_hooks(
                                    length, rot_angle, shape_props, concr_prop, 
                                    rebar_hook.start_hook, rebar_hook.end_hook, 
                                    rebar_hook.start_angle, rebar_hook.end_angle)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(
                                    mark_no, bendingshape, point1, point2,
                                    concr_bottom, concr_top, spacing)
    return rebars

# L shape using counting
def L_Shape_Count(rebar_prop, rebar_hook, diameter, length, height, rot_angle, concr_prop, 
                point1, point2, concr_bottom, concr_top, number, mark_no, reverse = False):

    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = Shape.create_l_shape_with_user_hooks(
                                    length, height, rot_angle, shape_props, concr_prop, 
                                    rebar_hook.start_hook, rebar_hook.end_hook, 
                                    rebar_hook.start_angle, rebar_hook.end_angle, reverse)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(
                                    mark_no, bendingshape, point1, point2,
                                    concr_bottom, concr_top, number)
    return rebars

# Open Stirrup using counting
def OpenStirrup_Count(rebar_prop, rebar_hook, diameter, length, height, rot_angle, concr_prop, 
                point1, point2, concr_bottom, concr_top, number):

    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = GeneralShapeBuilder.create_open_stirrup(
                                    length, height, rot_angle, shape_props, concr_prop,
                                    rebar_hook.start_hook, rebar_hook.end_hook, 
                                    rebar_hook.start_angle, rebar_hook.end_angle)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(
                                    2, bendingshape, point1, point2,
                                    concr_bottom, concr_top, number)
    return rebars

def OpenStirrupSpacing(rebar_prop, rebar_hook, diameter, length, width, rot_angle, concr_prop, 
                        point1, point2, concr_bottom, concr_top, spacing):

    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = GeneralShapeBuilder.create_open_stirrup(
                                    length, width, rot_angle, shape_props, concr_prop,
                                    rebar_hook.start_hook, rebar_hook.end_hook, 
                                    rebar_hook.start_angle, rebar_hook.end_angle)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(
                                    2, bendingshape, point1, point2,
                                    concr_bottom, concr_top, spacing)
    return rebars

# Open Stirrup with different cover top at end using counting
def OpenStirrup_with_coverend_Count(rebar_prop, rebar_hook, diameter, length, height, rot_angle, concr_prop, 
                coverend, point1, point2, concr_bottom, concr_top, number):

    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = Shape.create_open_stirrup_with_coverend(
                                    length, height, rot_angle, shape_props, concr_prop, coverend,
                                    rebar_hook.start_hook, rebar_hook.end_hook, 
                                    rebar_hook.start_angle, rebar_hook.end_angle)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(
                                    2, bendingshape, point1, point2,
                                    concr_bottom, concr_top, number)
    return rebars

# Close Stirrup using Spacing
def CloseStirrupSpacing(rebar_prop, rebar_hook, diameter, length, height, rot_angle, concr_prop, 
                point1, point2, concr_bottom, concr_top, spacing, mark_no=2):

    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = GeneralShapeBuilder.create_stirrup_with_user_hooks(
                                    length, height, rot_angle, shape_props, concr_prop,
                                    AllplanReinf.StirrupType.Column,
                                    rebar_hook.start_hook, rebar_hook.start_angle, 
                                    rebar_hook.end_hook, rebar_hook.end_angle)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(
                                    mark_no, bendingshape, point1, point2,
                                    concr_bottom, concr_top, spacing)
    return rebars

# Create freeform using Count
def Freeform_Count(rebar_prop, rebar_hook, diameter, points, rot_angle,
                        point1, point2, concr_bottom, concr_top, number, mark_no=2):
    
    shape_props     = ReinforcementShapeProperties.rebar(
                                    diameter, rebar_prop.bending_roller, 
                                    rebar_prop.steel_grade, rebar_prop.concr_grade,
                                    AllplanReinf.BendingShapeType.LongitudinalBar )

    bendingshape    = Shape.create_freeform_shape_with_user_hooks(
                                    points, rot_angle, shape_props,
                                    rebar_hook.start_hook, rebar_hook.end_hook, 
                                    rebar_hook.start_angle, rebar_hook.end_angle)

    rebars          = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(
                                    mark_no, bendingshape, point1, point2,
                                    concr_bottom, concr_top, number)

    return rebars
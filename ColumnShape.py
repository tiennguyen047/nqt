import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil


# Hook type from angle
def get_hook_type_from_angle(hook_type, hook_angle):
    if hook_type != -1:
        return hook_type
    if abs(hook_angle) < 134:
        return AllplanReinf.HookType.eAngle
    return  AllplanReinf.HookType.eStirrup

# L shape with user hooks
def create_l_shape_with_user_hooks(length, width, model_angles, shape_props,
                                    concrete_cover_props,
                                    start_hook       = 0,
                                    end_hook         = 0,
                                    start_hook_angle = 90.0,
                                    end_hook_angle   = 90.0,
                                    reverse = False):

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    if reverse:
        shape_builder.AddPoints([(AllplanGeo.Point2D(0, width), concrete_cover_props.left),
                             (AllplanGeo.Point2D(0, 0), concrete_cover_props.bottom),
                             (AllplanGeo.Point2D(length, 0), concrete_cover_props.right),
                             (concrete_cover_props.top)])
    else:
        shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover_props.left),
                             (AllplanGeo.Point2D(length, 0), concrete_cover_props.bottom),
                             (AllplanGeo.Point2D(length, width), concrete_cover_props.right),
                             (concrete_cover_props.top)])

    if start_hook >= 0:
        shape_builder.SetHookStart(start_hook, start_hook_angle,
                                   get_hook_type_from_angle(-1, start_hook_angle))

    if end_hook >= 0:
        shape_builder.SetHookEnd(end_hook, end_hook_angle,
                                 get_hook_type_from_angle(-1, end_hook_angle))

    shape = shape_builder.CreateShape(shape_props)


    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

# Open Stirrup with different cover top at end
def create_open_stirrup_with_coverend(length, width,
                        model_angles,
                        shape_props,
                        concrete_cover_props,
                        coverend,
                        start_hook       = 0,
                        end_hook         = 0,
                        start_hook_angle = 90.0,
                        end_hook_angle   = 90.0,
                        hook_type        = -1):


    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddPoints([(AllplanGeo.Point2D(0, width), concrete_cover_props.top),
                             (AllplanGeo.Point2D(0, 0), concrete_cover_props.left),
                             (AllplanGeo.Point2D(length, 0), concrete_cover_props.bottom),
                             (AllplanGeo.Point2D(length, width), concrete_cover_props.right),
                             (coverend)])

    if start_hook >= 0:
        shape_builder.SetHookStart(start_hook, start_hook_angle,
                                   get_hook_type_from_angle(hook_type, start_hook_angle))

    if end_hook >= 0:
        shape_builder.SetHookEnd(end_hook, end_hook_angle,
                                 get_hook_type_from_angle(hook_type, end_hook_angle))

    shape = shape_builder.CreateShape(shape_props)


    #----------------- Rotate the shape in the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

# Freeform shape with user hook
def create_freeform_shape_with_user_hooks(points, model_angles,
                                        shape_props,
                                        start_hook       = 0,
                                        end_hook         = 0,
                                        start_hook_angle = 90.0,
                                        end_hook_angle   = 90.0 ):

    shape_pol = AllplanGeo.Polyline3D()

    for point in points:
        shape_pol += point

    br_list = AllplanUtil.VecDoubleList()

    bero = shape_props.bending_roller

    br_list[:] = [bero, bero, bero, bero]

    shape = AllplanReinf.BendingShape(shape_pol, br_list, shape_props.diameter, shape_props.steel_grade, -1,
                                      AllplanReinf.BendingShapeType.BarSpacer)


    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

import NemAll_Python_Geometry as AllplanGeo

import math

################ Get points
def get2d_fr_3d(point3D):
    return AllplanGeo.Point2D(point3D.Values()[0], point3D.Values()[1])

def get2dangle_fr_3d(point3D1, point3D2):
    return AllplanGeo.CalcAngle(get2d_fr_3d(point3D1), get2d_fr_3d(point3D2))

def get_2d_distance(point3D1, point3D2):
    return abs(AllplanGeo.Point2D(point3D1).GetDistance(AllplanGeo.Point2D(point3D2)))

def get_3dpoint_fr_point_dist(point3D, distance, angle):
    x = point3D.Values()[0] + distance*math.cos(angle)
    y = point3D.Values()[1] + distance*math.sin(angle)
    return AllplanGeo.Point3D(x, y, point3D.Values()[2])

def get_2dpoint_fr_point_dist(point3D, distance, angle):
    x = point3D.Values()[0] + distance*math.cos(angle)
    y = point3D.Values()[1] + distance*math.sin(angle)
    return AllplanGeo.Point2D(x, y)

def addx_2d(point2D, x):
    return AllplanGeo.Point2D(point2D.Values()[0] + x, point2D.Values()[1])

def addy_2d(point2D, y):
    return AllplanGeo.Point2D(point2D.Values()[0], point2D.Values()[1] + y)

def addxy_2d(point2D, x, y):
    return AllplanGeo.Point2D(point2D.Values()[0] + x, point2D.Values()[1] + y)

def addx_3d(point3D, x):
    return AllplanGeo.Point3D(point3D.Values()[0] + x, point3D.Values()[1], point3D.Values()[2])

def addy_3d(point3D, y):
    return AllplanGeo.Point3D(point3D.Values()[0], point3D.Values()[1] + y, point3D.Values()[2])

def addz_3d(point3D, z):
    return AllplanGeo.Point3D(point3D.Values()[0], point3D.Values()[1], point3D.Values()[2] + z)

################# Get points from input
def get_min_points(point_list):
    return [point for point in point_list if round(point.Values()[2],0) == round(get_min_z(point_list),0)]

def arrange_y_points(point_list):
    return sorted(point_list, key=lambda point:point.Values()[1])

def get_first_point(point_list):
    first_pnt_list = [point for point in point_list if round(point.Values()[0],0) == round(get_min_x(point_list),0)]
    if len(first_pnt_list) == 1:
        return first_pnt_list[0]
    else:
        return [point for point in first_pnt_list if round(point.Values()[1],0) == round(get_min_y(first_pnt_list),0)][0]

def get_first_point_column(point_list):
    #get minx point
    first_pnt_list = [point for point in point_list if round(point.Values()[0],0) == round(get_min_x(point_list),0)]
    if len(first_pnt_list) == 1:
        first_point = first_pnt_list[0]
    else:
        first_point = [point for point in first_pnt_list if round(point.Values()[1],0) == round(get_min_y(first_pnt_list),0)][0]
    #check miny point, if miny point index is 2, get miny point.
    arrange_y = arrange_y_points(point_list)
    if arrange_y.index(first_point) > 1:
        first_point = arrange_y[0]
    return first_point

def get_angle_2_point3d(point1, point2):
    return AllplanGeo.CalcAngle(AllplanGeo.Point2D(point1), AllplanGeo.Point2D(point2))

def get_4_bottom_points(point_list):
    # Get only min z from list
    point_list  = get_min_points(point_list)
    # First point is min x point
    first_pnt   = get_first_point(point_list)

    # Third point is max distance point
    third_pnt   = [point for point in point_list if abs(first_pnt.GetDistance(point))\
                                        == get_max_distance(first_pnt, point_list)][0]
    # Fouth point is min distance point
    fouth_pnt   = [point for point in point_list if abs(first_pnt.GetDistance(point))\
                                        == get_min_distance(first_pnt, point_list)][0]
    # Second point is calculated by 3 rest points
    second_pnt  = first_pnt + AllplanGeo.Vector3D(fouth_pnt, third_pnt)
    # Return 4 points
    return [first_pnt, second_pnt, third_pnt, fouth_pnt]

def rearrange_bottom_points(point_list):
    # Rearrange for 4 points bottom
    angle       = AllplanGeo.CalcAngle( AllplanGeo.Point2D(point_list[0].Values()[0],
                                                    point_list[0].Values()[1]),
                                        AllplanGeo.Point2D(point_list[1].Values()[0],
                                                    point_list[1].Values()[1])).GetDeg()
    # TH1: Y0 >= Y3
    if (round(point_list[0].Values()[1],2) >= round(point_list[3].Values()[1],2)):
        return [point_list[3], point_list[2], point_list[1], point_list[0]]
    return point_list

def get_8_points(point_list):
    bottom_list = get_4_bottom_points(point_list)
    bottom_list = rearrange_bottom_points(bottom_list)
    z = get_max_z(point_list)
    return bottom_list + [change_z(point, z) for point in bottom_list]

def get_8_pnt_base_pnt(point_list, base_point_list):
    return rearrange_base_points(get_8_points(point_list), base_point_list)

def get_8_points_column(point_list):
    z = get_max_z(point_list)
    # Get only min z from list
    point_list  = get_min_points(point_list)
    # First point is min x point
    first_point = get_first_point_column(point_list)
    #get remain points by arrange angle
    point_list.remove(first_point)
    remain_points  = sorted(point_list, key = lambda point: get_angle_2_point3d(first_point, point).GetDeg())
    bottom_list = [first_point] + remain_points
    return bottom_list + [change_z(point, z) for point in bottom_list]

def rearrange_base_points(point_list, base_point_list):
    # Angle from first point to second point
    angle1      = AllplanGeo.CalcAngle( AllplanGeo.Point2D(point_list[0].Values()[0],
                                                    point_list[0].Values()[1]),
                                        AllplanGeo.Point2D(point_list[1].Values()[0],
                                                    point_list[1].Values()[1])).GetDeg()
    # Angle from first point to fouth point
    angle2      = AllplanGeo.CalcAngle( AllplanGeo.Point2D(point_list[0].Values()[0],
                                                    point_list[0].Values()[1]),
                                        AllplanGeo.Point2D(point_list[3].Values()[0],
                                                    point_list[3].Values()[1])).GetDeg()
    # Angle from base first point to second first point
    base_angle1 = AllplanGeo.CalcAngle( AllplanGeo.Point2D(base_point_list[0].Values()[0],
                                                    base_point_list[0].Values()[1]),
                                        AllplanGeo.Point2D(base_point_list[1].Values()[0],
                                                    base_point_list[1].Values()[1])).GetDeg()
    if abs(round(angle1,0)) == abs(round(base_angle1,0)):
        return point_list
    elif (abs(round(angle2,0)) == abs(round(base_angle1,0))):
        return [point_list[1], point_list[2], point_list[3], point_list[0],
                point_list[5], point_list[6], point_list[7], point_list[4]]
    elif (abs(round(angle2 + 180,0)) == abs(round(base_angle1,0))) or \
         (abs(round(angle2 - 180,0)) == abs(round(base_angle1,0))):
        return [point_list[3], point_list[0], point_list[1], point_list[2],
                point_list[7], point_list[4], point_list[5], point_list[6]]
    else:
        return []

def change_z(point, z):
    return AllplanGeo.Point3D(point.Values()[0], point.Values()[1], z)

def get_min_distance(point, point_list):
    return min([abs(point.GetDistance(ref_point)) for ref_point in point_list\
                if abs(point.GetDistance(ref_point)) != 0])

def get_max_distance(point, point_list):
    return max([abs(point.GetDistance(ref_point)) for ref_point in point_list])

def get_min_x(point_list):
    return min([point.Values()[0] for point in point_list])

def get_max_x(point_list):
    return max([point.Values()[0] for point in point_list])

def get_min_y(point_list):
    return min([point.Values()[1] for point in point_list])

def get_max_y(point_list):
    return max([point.Values()[1] for point in point_list])

def get_min_z(point_list):
    return min([point.Values()[2] for point in point_list])

def get_max_z(point_list):
    return max([point.Values()[2] for point in point_list])

def get_min_z_list(beam_list):
    return min([point.Values()[2] for beam in beam_list for point in beam])

def get_max_z_list(beam_list):
    return max([point.Values()[2] for beam in beam_list for point in beam])

def get_total_beam(beam_list):
    first_beam  = beam_list[0]
    last_beam   = beam_list[-1]
    minz        = get_min_z_list(beam_list)
    maxz        = get_max_z_list(beam_list)
    point1      = change_z(first_beam[0], minz)
    point2      = change_z(last_beam[1],  minz)
    point3      = change_z(last_beam[2],  minz)
    point4      = change_z(first_beam[3], minz)
    point5      = change_z(first_beam[0], maxz)
    point6      = change_z(last_beam[1],  maxz)
    point7      = change_z(last_beam[2],  maxz)
    point8      = change_z(first_beam[3], maxz)
    return [point1, point2, point3, point4, point5, point6, point7, point8]

def get_elevation_list(beam_list):
    return list(set([round(point.Values()[2],0) for beam in beam_list for point in beam]))

def check_above(below_points, above_points):
    """ check if 1 object is above of the another object """
    #check z
    max_below_z = get_max_z(below_points)
    min_above_z = get_min_z(above_points)
    if max_below_z > min_above_z:
        return False
    #check x
    min_below_x = get_min_x(below_points)
    min_above_x = get_min_x(above_points)
    max_below_x = get_max_x(below_points)
    max_above_x = get_max_x(above_points)
    if (min_below_x - 100 > min_above_x) or (max_below_x  + 100 < max_above_x):
        return False
    #check x
    min_below_y = get_min_y(below_points)
    min_above_y = get_min_y(above_points)
    max_below_y = get_max_y(below_points)
    max_above_y = get_max_y(above_points)
    if (min_below_y  - 100 > min_above_y) or (max_below_y  + 100 < max_above_y):
        return False
    return True

def get_above_object(below_points, above_points_list):
    """ check if 1 list of objects contain 1 above object of the another object """
    for above_points in above_points_list:
        if check_above(below_points, above_points):
            return above_points
    return None

def Change_x(point, x):
    return AllplanGeo.Point3D(x, point.Values()[1], point.Values()[2])

def Change_y(point, y):
    return AllplanGeo.Point3D(point.Values()[0], y, point.Values()[2])

def Change_z(point, z):
    return AllplanGeo.Point3D(point.Values()[0], point.Values()[1], z)

def Offset_x(point, x, angle):
    new_x = point.Values()[0] + x*math.cos(angle)
    new_y = point.Values()[1] + x*math.sin(angle)
    return AllplanGeo.Point3D(new_x, new_y, point.Values()[2])

def Offset_y(point, y, angle):
    new_x = point.Values()[0] + y*math.cos(AllplanGeo.Angle((90 + angle.GetDeg())/180*math.pi))
    new_y = point.Values()[1] + y*math.sin(AllplanGeo.Angle((90 + angle.GetDeg())/180*math.pi))
    return AllplanGeo.Point3D(new_x, new_y, point.Values()[2])

def Offset_xy(point, x, y, angle):
    offsetx = Offset_x(point, x, angle)
    return Offset_y(offsetx, y, angle)

def Offset_z(point, delta_z):
    return AllplanGeo.Point3D(point.Values()[0], point.Values()[1], point.Values()[2] + delta_z)

def MidPoint(point1, point2):
    return AllplanGeo.Point3D((point1.Values()[0] + point2.Values()[0])/2, (point1.Values()[1] + point2.Values()[1])/2, (point1.Values()[2] + point2.Values()[2])/2)
    

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_AllplanSettings as AllplanSettings

import math
import sys
import os
import json

# Import custom control module
import YT_Point_Control as Point_Control

path       = os.path.dirname(__file__)
userpath   = AllplanSettings.AllplanPaths.GetUsrPath()
Manuf_list = ['Halfen','Peikko', 'Schöck BOLE O', 'Schöck BOLE U', 'Schöck BOLE F']
Manuf_dict = {"Halfen":"HDB","Peikko":"PSB","Schöck BOLE O":"BOLE O","Schöck BOLE U":"BOLE U","Schöck BOLE F":"BOLE F"}
angle_dict = {1: (6, 3), -1: (6, 3), 5: (30/7, 30/8), 3: (18/5, 9/2)}

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Halfen Class!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class PunchingShear_Creator():
    def __init__(self, parent, point_list, geometry):
        # Custom parameters
        self.parent           = parent
        self.point_list       = point_list
        self.geometry         = geometry
        self.error            = False
        self.model_ele_list   = []
        self.com_prop         = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()
        self.get_parameters()

    def get_parameters(self):
        # Selected
        try:
            with open(r"{}/PunchingType.json".format(userpath), "r") as f:
                data = json.load(f)
                self.selected = data['Selected']
        except:
            self.error = True
        try:
            with open(r"{}/PunchingShear.json".format(userpath), "r") as f:
                self.PSS_data = json.load(f)
        except:
            self.error = True
        try:
            with open(r"{}/PunchingShearSpacing.json".format(userpath), "r") as f:
                self.PSS_spac = json.load(f)
        except:
            self.error = True

    def create(self):
        # Creating rails
        if self.geometry == "Rectangle":
            # Rectangle
            self.Length    = Point_Control.Get2D_Distance(self.point_list[0], self.point_list[1])
            self.Width     = Point_Control.Get2D_Distance(self.point_list[1], self.point_list[2])
            self.angle     = Point_Control.Get2D_Angle(self.point_list[0], self.point_list[1])
            self.Reference = self.point_list[0]
            self.create_direction()
            self.create_angle()
        else:
            # Circle
            self.Radius    = self.point_list[0].GetDistance(self.point_list[1])
            self.angle     = AllplanGeo.Angle()
            self.Reference = self.point_list[0]
            self.create_radius()

        # Creating group
        elementgroup = AllplanBasisElements.ElementGroupElement(
                self.com_prop, AllplanBasisElements.ElementGroupProperties(), self.model_ele_list)
        self.model_ele_list = [elementgroup]
        # Return list.
        return self.model_ele_list

    def create_radius(self):
        # Rail for circle column
        with open("{}/YT_PSS_Type.json".format(path), "r") as read_file:
            data = json.load(read_file)
            angle = int(data[self.selected]['Angle'])
            number = int(data[self.selected]['Number'])
            total_angle = math.pi/2*angle
            # Loop for each rail
            for i in range(number):
                # Full circle or part
                if angle == 4:
                    i_angle = total_angle/(number)*i
                else:
                    i_angle = total_angle/(number-1)*i
                # transform and create rail
                transform = self.create_transform(math.cos(i_angle)*self.Radius, math.sin(i_angle)*self.Radius, 0, i_angle)
                self.model_ele_list += self.create_one_rail(transform)

    def create_direction(self):
        # Rail direction Top Bottom Right Left
        with open("{}/YT_PSS_Type.json".format(path), "r") as read_file:
            data = json.load(read_file)
            # Rail in Top position
            top_number    = int(data[self.selected]['Top'])
            top_spacer    = self.PSS_data['Top_Bottom']
            left_spacer   = self.PSS_data['Left_Right']
            left_over     = (self.Length - top_spacer*(top_number - 1))/2
            for i in range(top_number):
                transform = self.create_transform(left_over + top_spacer * i, self.Width, 0, math.pi/2)
                self.model_ele_list += self.create_one_rail(transform)
            # Rail in Bot position
            bot_number    = int(data[self.selected]['Bottom'])
            left_over     = (self.Length - top_spacer*(bot_number - 1))/2
            for i in range(bot_number):
                transform = self.create_transform(left_over + top_spacer * i, 0, 0, -math.pi/2)
                self.model_ele_list += self.create_one_rail(transform)
            # Rail in Right position
            right_number  = int(data[self.selected]['Right'])
            left_over     = (self.Width - left_spacer*(right_number - 1))/2
            for i in range(right_number):
                transform = self.create_transform(self.Length, left_over + left_spacer * i, 0, 0)
                self.model_ele_list += self.create_one_rail(transform)
            # Rail in Left position
            left_number   = int(data[self.selected]['Left'])
            left_over     = (self.Width - left_spacer*(left_number - 1))/2
            for i in range(left_number):
                transform = self.create_transform(0, left_over + left_spacer * i, 0, math.pi)
                self.model_ele_list += self.create_one_rail(transform)

    def create_angle_type(self, x, y, z, angle_ratio, two_rail):
        if not two_rail:
            transform = self.create_transform(x, y, z, angle_ratio*math.pi/4) 
            self.model_ele_list += self.create_one_rail(transform)
        else:
            angle1, angle2 = angle_dict[angle_ratio]
            transform = self.create_transform(x, y, z, angle_ratio*math.pi/angle1) 
            self.model_ele_list += self.create_one_rail(transform)
            transform = self.create_transform(x, y, z, angle_ratio*math.pi/angle2) 
            self.model_ele_list += self.create_one_rail(transform)

    def create_angle(self):
        # Rail angle around column rectangle (max = 4)
        with open("{}/YT_PSS_Type.json".format(path), "r") as read_file:
            data = json.load(read_file)
            # Rail angle top left
            if int(data[self.selected]['Angletl']):
                self.create_angle_type(0, self.Width, 0, 3, self.PSS_data["Cor_Top_Left"])
            # Rail angle top right
            if int(data[self.selected]['Angletr']):
                self.create_angle_type(self.Length, self.Width, 0, 1, self.PSS_data["Cor_Top_Right"])
            # Rail angle bot right
            if int(data[self.selected]['Anglebr']):
                self.create_angle_type(self.Length, 0, 0, -1, self.PSS_data["Cor_Bot_Right"])
            # Rail angle bot left
            if int(data[self.selected]['Anglebl']):
                self.create_angle_type(0, 0, 0, 5, self.PSS_data["Cor_Bot_Left"])

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Creator Functions!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def create_one_rail(self, transform):
        rail = self.create_rail_type(transform, '1')
        if self.PSS_data['ItemsNumber'] == 1:
            return rail
        else:
            for num in range(2, self.PSS_data['ItemsNumber'] + 1):
                rail += self.create_rail_type(transform, str(num))
        return rail

    def get_offset(self, num):
        if num == 2:
            offset =    sum([self.PSS_spac[length] for length in self.PSS_spac.keys() 
                            if length[-1]=="1" and self.PSS_spac[length] != 0][1:]) # Except Number and 0
        elif num == 3:
            offset =    sum([self.PSS_spac[length] for length in self.PSS_spac.keys() 
                            if length[-1]=="1" and self.PSS_spac[length] != 0][1:]) + \
                        sum([self.PSS_spac[length] for length in self.PSS_spac.keys() 
                            if length[-1]=="2" and self.PSS_spac[length] != 0][1:])
        elif num == 4:
            offset =    sum([self.PSS_spac[length] for length in self.PSS_spac.keys() 
                            if length[-1]=="1" and self.PSS_spac[length] != 0][1:]) + \
                        sum([self.PSS_spac[length] for length in self.PSS_spac.keys() 
                            if length[-1]=="2" and self.PSS_spac[length] != 0][1:]) + \
                        sum([self.PSS_spac[length] for length in self.PSS_spac.keys() 
                            if length[-1]=="3" and self.PSS_spac[length] != 0][1:])
        else:
            offset = 0
        return offset

    def create_rail_type(self, transform, rail_type):
        # Stud spacing distance list
        rail_length = [self.PSS_spac[length] for length in self.PSS_spac.keys() 
                        if length[-1]==rail_type and self.PSS_spac[length] != 0][1:] # Except Number and 0
        # Creating rail
        total_length = sum(rail_length)
        offset = self.get_offset(int(rail_type))
        rail = self.create_rail(total_length, offset, transform)

        # Creating studs
        offset = offset
        for length in rail_length[:-1]: # Except End
            offset += length
            stud = self.create_stud(offset, transform)
            err, rail = AllplanGeo.MakeUnion(stud, rail)
        model_element = AllplanBasisElements.ModelElement3D(self.com_prop, rail)

        # Set the attributes for schedule.
        try:
            manu = Manuf_list[(self.PSS_data["Manufacturer"])]
            manu_type = Manuf_dict[manu]
        except:
            manu = "Wrong"
            manu_type = "Wrong"
        model_element.SetAttributes(AllplanBaseElements.Attributes([AllplanBaseElements.AttributeSet([
            AllplanBaseElements.AttributeString(208, self.attribute_list(rail_type)),
            AllplanBaseElements.AttributeString(575, "Punching Shear"),
            AllplanBaseElements.AttributeString(83, str(self.PSS_data["Pos_Name" + rail_type])),
            AllplanBaseElements.AttributeString(207, manu[:6]),
            AllplanBaseElements.AttributeString(1310, manu_type)
            ])]))

        return [model_element]

    def attribute_list(self, rail_type):
        rail_length = [self.PSS_spac[length] for length in self.PSS_spac.keys() 
                        if length[-1]==rail_type and self.PSS_spac[length] != 0]
        total_length = sum(rail_length[1:])
        detail_length = "/".join([str(i) for i in rail_length[1:]])
        fulltext = "{}/{}-{}/{}({})".format(
                    self.PSS_data['Diameter'],
                    self.PSS_data['Height'],
                    rail_length[0],
                    total_length,
                    detail_length)
        return fulltext

    def create_rail(self, length, offset, transfrom):
        """ Creating the rail and return
        """
        height   = self.PSS_data["Height"]
        reverse  = self.PSS_data["Reverse"]
        if reverse:
            base_transform = self.create_transform(offset, -15, -height, 0)
        else:
            base_transform = self.create_transform(offset, -15, 0, 0)
        axis = AllplanGeo.AxisPlacement3D()
        rail = AllplanGeo.BRep3D.CreateCuboid(axis, length, 30, 4)
        rail = AllplanGeo.Transform(rail, base_transform)
        rail = AllplanGeo.Transform(rail, transfrom)
        return rail

    def create_stud(self, offset, transfrom):
        """ Creating the stud geometry by revoved and return
        """
        # Stud curves
        radius   = self.PSS_data["Diameter"]/2
        height   = self.PSS_data["Height"]
        reverse  = self.PSS_data["Reverse"]
        polyline = AllplanGeo.Polyline3D()
        polyline += AllplanGeo.Point3D(0, 0, 0)
        polyline += AllplanGeo.Point3D(3*radius, 0, 0)
        polyline += AllplanGeo.Point3D(3*radius, 0, -6)
        polyline += AllplanGeo.Point3D(radius, 0, -15)
        polyline += AllplanGeo.Point3D(radius, 0, -(height - 15))
        polyline += AllplanGeo.Point3D(3*radius, 0, -(height - 6))
        polyline += AllplanGeo.Point3D(3*radius, 0, -height)
        polyline += AllplanGeo.Point3D(0, 0, -height)
        polyline += AllplanGeo.Point3D(0, 0, 0)
        polyline_rot = AllplanGeo.Move(polyline, AllplanGeo.Vector3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(offset, 15,0)))
        profiles = [polyline_rot]
        # Axis
        axis_line = AllplanGeo.Line3D(AllplanGeo.Point3D(offset, 15, 0), AllplanGeo.Point3D(offset, 15, 1))
        axis = AllplanGeo.Axis3D(axis_line)
        # Creating and return
        err, revolved = AllplanGeo.CreateRevolvedBRep3D(profiles, axis, AllplanGeo.Angle(math.pi*2), True, 0)
        if reverse:
            base_transform = self.create_transform(0, -15, 4, 0)
        else:
            base_transform = self.create_transform(0, -15, 0, 0)
        revolved = AllplanGeo.Transform(revolved, base_transform)
        revolved = AllplanGeo.Transform(revolved, transfrom)
        return revolved

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Support Functions!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def create_transform(self, x, y, z, angle):
        # Creating transform with reference point
        matrix = AllplanGeo.Matrix3D()
        matrix.Rotation(AllplanGeo.Line3D(AllplanGeo.Point3D(0,0,0), AllplanGeo.Point3D(0,0,1)), AllplanGeo.Angle(angle))
        matrix.SetTranslation(AllplanGeo.Vector3D(x, y, z))
        return matrix

    def Get_matrix3D(self):
        self.reference_X = self.Reference.Values()[0]
        self.reference_Y = self.Reference.Values()[1]
        # Matrix 3D Moving Rotation
        matrix = AllplanGeo.Matrix3D()
        matrix.Rotation(Point_Control.GetLine_from1point(self.point_list[0]), self.angle)
        matrix.SetTranslation(AllplanGeo.Vector3D(
                self.reference_X, self.reference_Y,
                self.PSS_data["Elevation"] -self.PSS_data["Offset"] - 4))
        return matrix





import math
import os
import sys

sys.path.append(os.path.dirname(__file__))

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_AllplanSettings as AllplanSettings
from StdReinfShapeBuilder.ConcreteCoverProperties import ConcreteCoverProperties
from StdReinfShapeBuilder.RotationAngles import RotationAngles
import NemAll_Python_Utility as AllplanUtil

import ColumnPlacement as Placement
import ColumnPoints as Points

__userpath__        = AllplanSettings.AllplanPaths.GetUsrPath()

class COLUMNREBAR():
    def __init__(self, doc, build_ele, column_list, current_pos):
        # Input parameters
        self.doc                        = doc
        self.build_ele                  = build_ele
        self.column_list                = column_list
        self.current_pos                = current_pos
        self.error                      = False
        self.Parameters()

    def Parameters(self):
        # Read Datas
        self.LoadRebarsData()

        # Other parameters
        self.column_bottom              = self.column_list[0].Values()[2]
        self.column_top                 = self.column_list[7].Values()[2]
        self.column_height              = self.column_top - self.column_bottom
        self.column_width               = abs(self.column_list[3].GetDistance(self.column_list[0]))
        self.column_length              = abs(self.column_list[0].GetDistance(self.column_list[1]))
        self.angle                      = AllplanGeo.CalcAngle(AllplanGeo.Point2D(self.column_list[0]) , AllplanGeo.Point2D(self.column_list[1]))
        self.rebar_prop                 = Placement.Rebar_prop(4, 4, 4)
        self.rebar_hook                 = Placement.Rebar_hook(-1, -1, -1, -1)
        self.stir_hook                  = Placement.Rebar_hook(self.stir_hook_len, self.stir_hook_len, self.stir_hook_ang, self.stir_hook_ang)
        self.concr_prop                 = ConcreteCoverProperties.all(self.concr_cover)

    def LoadRebarsData(self):
        """ load rebars data from json file """
        # Vertical Longit
        self.concr_cover        = self.build_ele.Concr_Cover.value
        self.concr_grade        = self.build_ele.Concr_Grade.value
        self.slab_thickness     = self.build_ele.Slab_Above.value
        #rebar
        self.main_dia           = self.build_ele.Main_Diameter.value
        self.main_crank         = self.build_ele.Main_Crank.value
        self.main_crank_len     = self.build_ele.Main_Crank_Distance.value
        self.main_stt           = self.build_ele.Main_Starter.value

        self.addX_num           = self.build_ele.Add_X_Number.value
        self.addX_dia           = self.build_ele.Add_X_Diameter.value
        self.addX_crank         = self.build_ele.AddX_Crank.value
        self.addX_crank_len     = self.build_ele.AddX_Crank_Distance.value
        self.addX_stt           = self.build_ele.AddX_Starter.value

        self.addY_num           = self.build_ele.Add_Y_Number.value
        self.addY_dia           = self.build_ele.Add_Y_Diameter.value
        self.addY_crank         = self.build_ele.AddY_Crank.value
        self.addY_crank_len     = self.build_ele.AddY_Crank_Distance.value
        self.addY_stt           = self.build_ele.AddY_Starter.value

        #main stirrup
        self.stir_main_dia      = self.build_ele.Main_Stirrup_Diameter.value
        self.stir_main_spc      = self.build_ele.Main_Stirrup_Spacing.value
        self.stir_hook_ang      = self.build_ele.Hook_Angle.value
        self.stir_hook_len      = self.build_ele.Hook_Length.value
        #additional stirrup top
        self.stir_addtop_chk    = self.build_ele.Add_Stirrup_Top.value
        self.stir_addtop_len    = self.build_ele.Add_Stirrup_Top_Length.value
        self.stir_addtop_spc    = self.build_ele.Add_Stirrup_Top_Spacing.value
        #additional stirrup bot
        self.stir_addbot_chk    = self.build_ele.Add_Stirrup_Bot.value
        self.stir_addbot_len    = self.build_ele.Add_Stirrup_Bot_Length.value
        self.stir_addbot_spc    = self.build_ele.Add_Stirrup_Bot_Spacing.value
            
    def check_input(self):
        # Check b and h
        if (self.column_length/self.column_width) > 4 or (self.column_width/self.column_length) > 4:
            AllplanUtil.ShowMessageBox("Please check again.\nIf h/b > 4 the element is classified as a wall.", AllplanUtil.MB_OK)

        # Check width and length minimum
        if min(round(self.column_length,1), round(self.column_width,1)) < 200:
            AllplanUtil.ShowMessageBox("Please check again.\nColumn Width is now smaller than 200", AllplanUtil.MB_OK)
            self.error = True

    def check_output(self):
        # Check maximum reinforcement
        Asmax                   = 0.09*self.column_length*self.column_width/100 # change to centimet
        steel_area              = 4*0.00785*(self.main_dia**2) + self.addX_num*0.00785*(self.addX_dia**2)\
                                    + self.addY_num*0.00785*(self.addY_dia**2)
        if steel_area           > Asmax:
            AllplanUtil.ShowMessageBox("Please check again.\nMax Column Reinforcement Area is 9%! ", AllplanUtil.MB_OK)
            self.error          = True

    def OnCheckError(self):
        """ checking column parameters and rebars """
        self.check_input()
        self.check_output()
        return self.error

    def Reinforcement(self):
        """ create rebars """
        Rebar_List = []
        #Stirrup
        Rebar_List += self.Stirrup()
        #Main
        if self.main_crank:
            Rebar_List += self.MainRebarCrank()
        else:
            Rebar_List += self.MainRebar(self.column_height + self.slab_thickness + self.main_stt)
        #AddX
        if self.addX_crank:
            Rebar_List += self.AdditionalXCrank()
        else:
            Rebar_List += self.AdditionalX(self.column_height + self.slab_thickness + self.addX_stt)
        #AddY
        if self.addY_crank:
            Rebar_List += self.AdditionalYCrank()
        else:
            Rebar_List += self.AdditionalY(self.column_height + self.slab_thickness + self.addY_stt)
        return Rebar_List

    def Stirrup(self):
        """ stirrup """
        Rebar_List      = []
        diameter        = self.stir_main_dia
        length          = self.column_length
        width           = self.column_width
        rot_angle       = RotationAngles(0, 0, self.angle.GetDeg())

        #Check if having Stirrup Top
        if (self.stir_addtop_chk):
            start_point = Points.Offset_z(self.column_list[4], -float(self.stir_addtop_len))
            end_point   = self.column_list[4]
            stir_top    = Placement.CloseStirrupSpacing(self.rebar_prop, self.stir_hook, diameter, length,
                                                        width, rot_angle, self.concr_prop, 
                                                        start_point, end_point, self.concr_cover, self.concr_cover,
                                                        self.stir_addtop_spc, mark_no=self.current_pos+12)
            Rebar_List.append(stir_top)
        else:
            self.stir_addtop_len = 0

        #Check if having Stirrup Bot
        if (self.stir_addbot_chk):
            start_point = self.column_list[0]
            end_point   = Points.Offset_z(self.column_list[0], float(self.stir_addbot_len))
            stir_bot    = Placement.CloseStirrupSpacing(self.rebar_prop, self.stir_hook, diameter, length,
                                                        width, rot_angle, self.concr_prop, 
                                                        start_point, end_point, self.concr_cover, self.concr_cover,
                                                        self.stir_addbot_spc, mark_no=self.current_pos+13)
            Rebar_List.append(stir_bot)
        else:
            self.stir_addbot_len = 0

        #main stirrup
        start_point     = Points.Offset_z(self.column_list[0], float(self.stir_addbot_len))
        end_point       = Points.Offset_z(self.column_list[4], -float(self.stir_addtop_len))
        stir_main       = Placement.CloseStirrupSpacing(self.rebar_prop, self.stir_hook, diameter, length,
                                                        width, rot_angle, self.concr_prop, 
                                                        start_point, end_point, self.concr_cover, self.concr_cover,
                                                        self.stir_main_spc, mark_no=self.current_pos+11)
        Rebar_List.append(stir_main)

        return Rebar_List

    def MainRebar(self, height):
        """ create main straight rebars """
        Rebar_List          = []
        offset              = self.concr_cover + self.main_dia/2 + self.stir_main_dia + 5
        #first rebar
        main_rebar          =  self.StraightMainRebar(self.column_list[0], height, offset_x=offset, offset_y=offset-self.main_dia/2)
        Rebar_List.append(main_rebar)
        #second rebar
        main_rebar          =  self.StraightMainRebar(self.column_list[1], height, offset_x=-offset, offset_y=offset-self.main_dia/2)
        Rebar_List.append(main_rebar)
        #third rebar
        main_rebar          =  self.StraightMainRebar(self.column_list[2], height, offset_x=-offset, offset_y=-offset+self.main_dia/2)
        Rebar_List.append(main_rebar)
        #fouth rebar
        main_rebar          =  self.StraightMainRebar(self.column_list[3], height, offset_x=offset, offset_y=-offset+self.main_dia/2)
        Rebar_List.append(main_rebar)
        return Rebar_List

    def MainRebarWithCrank(self):
        """ main rebar with crank option """
        Rebar_List          = []
        offset              = self.concr_cover + self.main_dia/2 + self.stir_main_dia + 5
        #first rebar
        start_point         = Points.Offset_xy(self.column_list[0], offset-self.main_dia/2, offset, self.angle)
        Rebar_List.append(self.CrankMainRebar(start_point, index=0, delta_angle=0))
        #second rebar
        start_point         = Points.Offset_xy(self.column_list[1], -offset-self.main_dia/2, offset, self.angle)
        Rebar_List.append(self.CrankMainRebar(start_point, index=1, delta_angle=0, ratio_x=-1))
        #third rebar
        start_point         = Points.Offset_xy(self.column_list[2], -offset-self.main_dia/2, -offset, self.angle)
        Rebar_List.append(self.CrankMainRebar(start_point, index=2, delta_angle=0, ratio_x=-1, ratio_y=-1))
        #fouth rebar
        start_point         = Points.Offset_xy(self.column_list[3], offset-self.main_dia/2, -offset, self.angle)
        Rebar_List.append(self.CrankMainRebar(start_point, index=3, delta_angle=0, ratio_y=-1))
        return Rebar_List

    def AdditionalX(self, height):
        """ additional straight rebar X direction """
        Rebar_List          = []
        rot_anglex          = RotationAngles(0, -90, self.angle.GetDeg())
        offset              = self.concr_cover + self.stir_main_dia
        offset_distancex    = offset + (self.column_length - 2*offset)/(self.addX_num+1)
        #firstx rebar
        first_x             = self.StraightAdditional(self.addX_dia, height, self.column_list[0], self.column_list[1],
                                                       self.addX_num, rot_anglex, offset=offset,  offset_side=offset_distancex, mark_num=21)
        Rebar_List.append(first_x)
        #secondx rebar
        second_x            = self.StraightAdditional(self.addX_dia, height, self.column_list[3], self.column_list[2],
                                                       self.addX_num, rot_anglex, offset=-offset, offset_side=offset_distancex, mark_num=21)
        Rebar_List.append(second_x)

        return Rebar_List

    def AdditionalY(self, height):
        """ additional straight rebar Y direction """
        Rebar_List          = []
        rot_angley          = RotationAngles(90, -90, self.angle.GetDeg())
        offset              = self.concr_cover + self.stir_main_dia
        offset_distancey    = offset + (self.column_width - 2*offset)/(self.addY_num+1)
        #firsty rebar
        first_y             = self.StraightAdditional(self.addY_dia, height, self.column_list[1], self.column_list[2],
                                                       self.addY_num, rot_angley, offset=offset,  offset_side=offset_distancey)
        Rebar_List.append(first_y)
        #secondy rebar
        second_y            = self.StraightAdditional(self.addY_dia, height, self.column_list[0], self.column_list[3],
                                                       self.addY_num, rot_angley, offset=-offset, offset_side=offset_distancey)
        Rebar_List.append(second_y)

        return Rebar_List

    def MainRebarCrank(self):
        """ main rebar with crank """
        Rebar_List                  = []
        offset                      = self.concr_cover + self.stir_main_dia

        #first rebar
        Rebar_List.append(self.CrankRebar(self.main_dia, self.column_list[0], self.column_list[1], 45,
                                                1, crank_len=self.main_crank_len, stater=self.main_stt,
                                                offset_y=offset + self.main_dia/2, offset_side=offset))
        #second rebar
        Rebar_List.append(self.CrankRebar(self.main_dia, self.column_list[1], self.column_list[0], 135,
                                                1, crank_len=self.main_crank_len, stater=self.main_stt,
                                                offset_y=offset + self.main_dia/2, offset_side=offset))
        #third rebar
        Rebar_List.append(self.CrankRebar(self.main_dia, self.column_list[2], self.column_list[3], -135,
                                                1, crank_len=self.main_crank_len, stater=self.main_stt,
                                                offset_y=-offset - self.main_dia/2, offset_side=offset))
        #fouth rebar
        Rebar_List.append(self.CrankRebar(self.main_dia, self.column_list[3], self.column_list[2], -45,
                                                1, crank_len=self.main_crank_len, stater=self.main_stt,
                                                offset_y=-offset - self.main_dia/2, offset_side=offset))
        return Rebar_List

    def AdditionalXCrank(self):
        """ additional X with crank """
        Rebar_List                  = []
        offset                      = self.concr_cover + self.stir_main_dia
        offset_distancex            = offset + (self.column_length - 2*offset)/(self.addX_num+1)
        offset_distancey            = offset + (self.column_width  - 2*offset)/(self.addY_num+1)

        #firstx rebar
        Rebar_List.append(self.CrankRebar(self.addX_dia, self.column_list[0], self.column_list[1], 90,
                                                self.addX_num, crank_len=self.addX_crank_len, stater=self.addX_stt,
                                                offset_y=offset + self.addX_dia/2, offset_side=offset_distancex))
        #secondx rebar
        Rebar_List.append(self.CrankRebar(self.addX_dia, self.column_list[3], self.column_list[2], -90,
                                                self.addX_num, crank_len=self.addX_crank_len, stater=self.addX_stt,
                                                offset_y=-offset - self.addX_dia/2, offset_side=offset_distancex))

        return Rebar_List

    def AdditionalYCrank(self):
        """ additional Y with crank """
        Rebar_List                  = []
        offset                      = self.concr_cover + self.stir_main_dia
        offset_distancex            = offset + (self.column_length - 2*offset)/(self.addX_num+1)
        offset_distancey            = offset + (self.column_width  - 2*offset)/(self.addY_num+1)

        #firsty rebar
        Rebar_List.append(self.CrankRebar(self.addY_dia, self.column_list[1], self.column_list[2], 180,
                                               self.addY_num, crank_len=self.addY_crank_len, stater=self.addY_stt,
                                               offset_x=-offset - self.addY_dia/2, offset_side=offset_distancey))
        #secondy rebar
        Rebar_List.append(self.CrankRebar(self.addY_dia, self.column_list[0], self.column_list[3], 0,
                                               self.addY_num, crank_len=self.addY_crank_len, stater=self.addY_stt,
                                               offset_x=offset + self.addY_dia/2, offset_side=offset_distancey))

        return Rebar_List

    ########################################################## SUPPORT FUNCTION ###################################################

    def CrankRebar(self, diameter, start_point, end_point, delta_angle, number, crank_len=100, stater=0,
                       index=0, offset_width=0, offset_x=0, offset_y=0, offset_side=0):
        """ create crank additional """
        #offset startpoint and endpoint
        start_point         = Points.Offset_xy(start_point, offset_x, offset_y, self.angle)
        end_point           = Points.Offset_xy(end_point,   offset_x, offset_y, self.angle)

        #get crank points
        points              = self.CrankPoints(AllplanGeo.Point3D(), self.column_height, crank_len,
                                                self.slab_thickness + 5, stater)

        #create crank rebar
        rot_angle           = RotationAngles(delta_angle -90, -90, self.angle.GetDeg())
        addrebar            = Placement.Freeform_Count(self.rebar_prop, self.rebar_hook, diameter, points, rot_angle,
                                                start_point, end_point, offset_side, offset_side, number, mark_no=2)
        return addrebar

    def StraightAdditional(self, diameter, height, start_point, end_point, number, rot_angle, offset=0, offset_side=0, mark_num=2):
        """ create straghit additional """
        concr_prop          = ConcreteCoverProperties(0, 0, 0, offset)
        straghit_rebar      = Placement.LongitCount(self.rebar_prop, self.rebar_hook, diameter, height, rot_angle, concr_prop, 
                                                    start_point, end_point, offset_side, offset_side, number, mark_num)
        return straghit_rebar

    def StraightMainRebar(self, start_point, height, offset_x=0, offset_y=0):
        """ create straghit main rebar """
        end_point           = Points.Offset_x(start_point, 1000, self.angle)
        diameter            = self.main_dia
        concr_prop          = ConcreteCoverProperties(0, self.concr_cover, 0, offset_y)
        rot_angle           = RotationAngles(0, -90, self.angle.GetDeg())
        straghit_rebar      = Placement.LongitCount(self.rebar_prop, self.rebar_hook, diameter, height, rot_angle, concr_prop, 
                                                    start_point, end_point, offset_x-diameter/2, -diameter/2, 1)
        return straghit_rebar

    def CrankPoints(self, start_point, length, crank_width, crank_height, remain_length):
        """ get crank points for mian rebar of the column with column above """
        second_point = start_point  + AllplanGeo.Point3D(length, 0, 0)
        third_point  = second_point + AllplanGeo.Point3D(crank_height, crank_width, 0)
        fouth_point  = third_point  + AllplanGeo.Point3D(remain_length, 0, 0)
        return [start_point, second_point, third_point, fouth_point]

    def GetStartPointMain(self, start_point, concrete_cover, stir_diameter, rebar_diameter, offset_diameter=0, ratio_x=1, ratio_y=1):
        """ get the startpoint for main rebar """
        point3d = Points.Offset_xy(start_point, ratio_x*(concrete_cover + stir_diameter + rebar_diameter/2 + offset_diameter),
                                                 ratio_y*(concrete_cover + stir_diameter + rebar_diameter/2 + offset_diameter), self.angle)
        return AllplanGeo.Point2D(point3d)

    def GetStartPointAdd(self, start_point, concrete_cover, stir_diameter, rebar_diameter, offset_diameter=0, ratio_x=1, ratio_y=1):
        """ get the startpoint for additional rebar """
        point3d = Points.Offset_xy(start_point, ratio_x*(concrete_cover + stir_diameter + rebar_diameter/2 + offset_diameter),
                                                 ratio_y*(concrete_cover + stir_diameter + rebar_diameter/2 + offset_diameter), self.angle)
        return AllplanGeo.Point2D(point3d)


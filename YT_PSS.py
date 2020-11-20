# Import Python default module
import os
import sys
import json

sys.path.append(os.path.dirname(__file__))

# Import custom module
import YT_PSS_Creator as Creator

# Import Allplan module
from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import NemAll_Python_AllplanSettings as AllplanSettings

from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename

__userpath__    = AllplanSettings.AllplanPaths.GetUsrPath()
__currentpath__ = os.path.dirname(__file__)
last_setting    = "PunchingShear_Last_Setting.json"

def check_allplan_version(build_ele, version):
    del build_ele
    del version
    return True

def create_element(build_ele, doc):
    return ([], None, None)

def create_interactor(coord_input, pyp_path, str_table_service):
    return Interactor(coord_input, pyp_path, str_table_service)


class Interactor():
    def __init__(self, coord_input, pyp_path, str_table_service):
        self.coord_input       = coord_input
        self.pyp_path          = pyp_path
        self.str_table_service = str_table_service
        self.doc               = coord_input.GetInputViewDocument()
        self.stt               = ''
        self.point_list        = []
        self.mess_dict         = {0:'first point', 1:'second point', 2:'third point or finish', 
                                    3: 'Finish'}
        self.show_palette("Selection")

    def GetSettingData(self):
        """ get current setting data """
        data = {}

        #general
        data['Elevation']               = self.build_ele.Elevation.value
        data['Offset']                  = self.build_ele.Offset.value
        data['Manufacturer']            = self.build_ele.Manufacturer.value
        data['TopBottomSpacing']        = self.build_ele.TopBottomSpacing.value
        data['LeftRightSpacing']        = self.build_ele.LeftRightSpacing.value
        #round rail
        data['Angle']                   = self.build_ele.Angle.value
        data['RotateAngle']             = self.build_ele.RotateAngle.value
        data['RoundNumber']             = self.build_ele.RoundNumber.value
        #corner rail
        data['Corner1']                 = self.build_ele.Corner1.value
        data['Corner2']                 = self.build_ele.Corner2.value
        data['Corner3']                 = self.build_ele.Corner3.value
        data['Corner4']                 = self.build_ele.Corner4.value
        data['MiddleA']                 = self.build_ele.MiddleA.value
        data['MiddleB']                 = self.build_ele.MiddleB.value
        data['MiddleC']                 = self.build_ele.MiddleC.value
        data['MiddleD']                 = self.build_ele.MiddleD.value
        #rail
        data['Diameter']                = self.build_ele.Diameter.value
        data['Height']                  = self.build_ele.Height.value
        data['Reverse']                 = self.build_ele.Reverse.value
        data['NumberOfItems']           = self.build_ele.NumberOfItems.value
        #first item
        data['FirstPosName']            = self.build_ele.FirstPosName.value
        data['FirstNumberOfStuds']      = self.build_ele.FirstNumberOfStuds.value
        data['FirstStart']              = self.build_ele.FirstStart.value
        data['FirstDistance1']          = self.build_ele.FirstDistance1.value
        data['FirstDistance2']          = self.build_ele.FirstDistance2.value
        data['FirstDistance3']          = self.build_ele.FirstDistance3.value
        data['FirstDistance4']          = self.build_ele.FirstDistance4.value
        data['FirstDistance5']          = self.build_ele.FirstDistance5.value
        data['FirstDistance6']          = self.build_ele.FirstDistance6.value
        data['FirstEnd']                = self.build_ele.FirstEnd.value
        #second item
        data['SecondPosName']           = self.build_ele.SecondPosName.value
        data['SecondNumberOfStuds']     = self.build_ele.SecondNumberOfStuds.value
        data['SecondStart']             = self.build_ele.SecondStart.value
        data['SecondDistance1']         = self.build_ele.SecondDistance1.value
        data['SecondDistance2']         = self.build_ele.SecondDistance2.value
        data['SecondDistance3']         = self.build_ele.SecondDistance3.value
        data['SecondDistance4']         = self.build_ele.SecondDistance4.value
        data['SecondDistance5']         = self.build_ele.SecondDistance5.value
        data['SecondDistance6']         = self.build_ele.SecondDistance6.value
        data['SecondEnd']               = self.build_ele.SecondEnd.value
        #third item
        data['ThirdPosName']            = self.build_ele.ThirdPosName.value
        data['ThirdNumberOfStuds']      = self.build_ele.ThirdNumberOfStuds.value
        data['ThirdStart']              = self.build_ele.ThirdStart.value
        data['ThirdDistance1']          = self.build_ele.ThirdDistance1.value
        data['ThirdDistance2']          = self.build_ele.ThirdDistance2.value
        data['ThirdDistance3']          = self.build_ele.ThirdDistance3.value
        data['ThirdDistance4']          = self.build_ele.ThirdDistance4.value
        data['ThirdDistance5']          = self.build_ele.ThirdDistance5.value
        data['ThirdDistance6']          = self.build_ele.ThirdDistance6.value
        data['ThirdEnd']                = self.build_ele.ThirdEnd.value
        #fouth item
        data['FouthPosName']            = self.build_ele.FouthPosName.value
        data['FouthNumberOfStuds']      = self.build_ele.FouthNumberOfStuds.value
        data['FouthStart']              = self.build_ele.FouthStart.value
        data['FouthDistance1']          = self.build_ele.FouthDistance1.value
        data['FouthDistance2']          = self.build_ele.FouthDistance2.value
        data['FouthDistance3']          = self.build_ele.FouthDistance3.value
        data['FouthDistance4']          = self.build_ele.FouthDistance4.value
        data['FouthDistance5']          = self.build_ele.FouthDistance5.value
        data['FouthDistance6']          = self.build_ele.FouthDistance6.value
        data['FouthEnd']                = self.build_ele.FouthEnd.value

        return data

    def LoadSettingData(self, data):
        """ load from setting data """
        #general
        self.build_ele.Elevation.value              = data['Elevation']
        self.build_ele.Offset.value                 = data['Offset']
        self.build_ele.Manufacturer.value           = data['Manufacturer']
        self.build_ele.TopBottomSpacing.value       = data['TopBottomSpacing']
        self.build_ele.LeftRightSpacing.value       = data['LeftRightSpacing']
        #round rail
        self.build_ele.Angle.value                  = data['Angle']
        self.build_ele.RotateAngle.value            = data['RotateAngle']
        self.build_ele.RoundNumber.value            = data['RoundNumber']
        #corner rail
        self.build_ele.Corner1.value                = data['Corner1']
        self.build_ele.Corner2.value                = data['Corner2']
        self.build_ele.Corner3.value                = data['Corner3']
        self.build_ele.Corner4.value                = data['Corner4']
        self.build_ele.MiddleA.value                = data['MiddleA']
        self.build_ele.MiddleB.value                = data['MiddleB']
        self.build_ele.MiddleC.value                = data['MiddleC']
        self.build_ele.MiddleD.value                = data['MiddleD']
        #rail
        self.build_ele.Diameter.value               = data['Diameter']
        self.build_ele.Height.value                 = data['Height']
        self.build_ele.Reverse.value                = data['Reverse']
        self.build_ele.NumberOfItems.value          = data['NumberOfItems']
        #first item
        self.build_ele.FirstPosName.value           = data['FirstPosName']
        self.build_ele.FirstNumberOfStuds.value     = data['FirstNumberOfStuds']
        self.build_ele.FirstStart.value             = data['FirstStart']
        self.build_ele.FirstDistance1.value         = data['FirstDistance1']
        self.build_ele.FirstDistance2.value         = data['FirstDistance2']
        self.build_ele.FirstDistance3.value         = data['FirstDistance3']
        self.build_ele.FirstDistance4.value         = data['FirstDistance4']
        self.build_ele.FirstDistance5.value         = data['FirstDistance5']
        self.build_ele.FirstDistance6.value         = data['FirstDistance6']
        self.build_ele.FirstEnd.value               = data['FirstEnd']
        #second item
        self.build_ele.SecondPosName.value          = data['SecondPosName']
        self.build_ele.SecondNumberOfStuds.value    = data['SecondNumberOfStuds']
        self.build_ele.SecondStart.value            = data['SecondStart']
        self.build_ele.SecondDistance1.value        = data['SecondDistance1']
        self.build_ele.SecondDistance2.value        = data['SecondDistance2']
        self.build_ele.SecondDistance3.value        = data['SecondDistance3']
        self.build_ele.SecondDistance4.value        = data['SecondDistance4']
        self.build_ele.SecondDistance5.value        = data['SecondDistance5']
        self.build_ele.SecondDistance6.value        = data['SecondDistance6']
        self.build_ele.SecondEnd.value              = data['SecondEnd']
        #third item
        self.build_ele.ThirdPosName.value           = data['ThirdPosName']
        self.build_ele.ThirdNumberOfStuds.value     = data['ThirdNumberOfStuds']
        self.build_ele.ThirdStart.value             = data['ThirdStart']
        self.build_ele.ThirdDistance1.value         = data['ThirdDistance1']
        self.build_ele.ThirdDistance2.value         = data['ThirdDistance2']
        self.build_ele.ThirdDistance3.value         = data['ThirdDistance3']
        self.build_ele.ThirdDistance4.value         = data['ThirdDistance4']
        self.build_ele.ThirdDistance5.value         = data['ThirdDistance5']
        self.build_ele.ThirdDistance6.value         = data['ThirdDistance6']
        self.build_ele.ThirdEnd.value               = data['ThirdEnd']
        #fouth item
        self.build_ele.FouthPosName.value           = data['FouthPosName']
        self.build_ele.FouthNumberOfStuds.value     = data['FouthNumberOfStuds']
        self.build_ele.FouthStart.value             = data['FouthStart']
        self.build_ele.FouthDistance1.value         = data['FouthDistance1']
        self.build_ele.FouthDistance2.value         = data['FouthDistance2']
        self.build_ele.FouthDistance3.value         = data['FouthDistance3']
        self.build_ele.FouthDistance4.value         = data['FouthDistance4']
        self.build_ele.FouthDistance5.value         = data['FouthDistance5']
        self.build_ele.FouthDistance6.value         = data['FouthDistance6']
        self.build_ele.FouthEnd.value               = data['FouthEnd']

    def SaveLastSetting(self):
        #save setting as favorite file
        with open(r"{}\{}".format(__currentpath__, last_setting), 'w') as f:
            data = self.GetSettingData()
            json.dump(data, f)


    def LoadLastSetting(self):
        #load favorite file setting
        with open(r"{}\{}".format(__currentpath__, last_setting), 'r') as f:
            data = json.load(f)
            self.LoadSettingData(data)
            self.palette_service.update_palette(0, False)

    def SaveSettingAsFavorite(self):
        """ save setting as favorite
        """
        root = Tk()
        file = asksaveasfilename(parent=root, defaultextension=".json",
                                    filetypes=(("setting file", "*.json"),("All Files", "*.*") ))

        if file:
            with open(file, 'w') as f:
                data = self.GetSettingData()
                json.dump(data, f)
        root.destroy()

    def LoadSettingAsFavorite(self):
        """ load favorite setting file
        """
        root = Tk()
        file = askopenfilename(parent=root, defaultextension=".json",
                                    filetypes=(("setting file", "*.json"),("All Files", "*.*") ))

        if file:
            with open(file, 'r') as f:
                data = json.load(f)
                self.LoadSettingData(data)
                self.palette_service.update_palette(0, False)
        root.destroy()

    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        # Get Point input
        input_point = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info).GetPoint()
        if self.coord_input.IsMouseMove(mouse_msg):
            # Show the Preview
            self.draw_preview()
        else:
            # Show messeage
            self.point_list.append(input_point)
            self.input_messeage()
        return True

    def on_control_event(self, event_id):
        #show palette
        if event_id == 1000:
            self.check_input()
        #create punchingshear
        if event_id == 1001:
            self.Draw_PSS()
            self.SaveLastSetting()
        #save setting
        if event_id == 3001:
            try:
                self.SaveSettingAsFavorite()
            except Exception as e:
                AllplanUtil.ShowMessageBox("Save setting failed: {}".format(e), AllplanUtil.MB_OK)

        #load setting
        elif event_id == 3002:
            try:
                self.LoadSettingAsFavorite()
            except Exception as e:
                AllplanUtil.ShowMessageBox("Load setting failed: {}".format(e), AllplanUtil.MB_OK)

    def on_preview_draw(self):
        pass

    def on_mouse_leave(self):
        pass

    def on_cancel_function(self):
        self.palette_service.close_palette()
        return True

    def show_palette(self, palette):
        result, self.build_ele_script, self.build_ele_list, self.control_props_list,    \
            self.build_ele_composite, part_name, self.file_name = \
            BuildingElementService().read_data_from_pyp(self.pyp_path + "\\" + "{}.pal".format(palette),
                                                      self.str_table_service.str_table, False, 
                                                      self.str_table_service.material_str_table)

        if not result:
            return True

        self.palette_service = BuildingElementPaletteService(self.build_ele_list, self.build_ele_composite,
                                                             self.build_ele_script,
                                                             self.control_props_list, self.file_name)

        self.palette_service.show_palette(part_name)
        self.build_ele = self.build_ele_list[0]

        # Show messenger
        self.input_messeage()

    def on_reset(self):
        self.point_list = []
        self.input_messeage()

    def input_messeage(self):
        self.coord_input.InitFirstElementInput(
            AllplanIFW.InputStringConvert(
            "Total input is {}. Please Choose {}".format(
            min(len(self.point_list), 3),
            self.mess_dict[min(len(self.point_list), 3)])))
            
    def check_input(self):
        if self.point_list == []:
            self.coord_input.InitFirstElementInput(
                AllplanIFW.InputStringConvert("Input is empty. Please input points"))
        elif len(self.point_list) == 1:
            self.coord_input.InitFirstElementInput(
                AllplanIFW.InputStringConvert("Not enough points. Please input the second point"))
        elif len(self.point_list) == 2:
            self.coord_input.InitFirstElementInput(
                AllplanIFW.InputStringConvert("Total input point is 2. Halfen type will be Circle"))
            self.geometry = "Circle"
            self.palette_service.close_palette()
            self.show_palette("PunchingShear")
            self.build_ele.IsRectangle.value = False
            self.palette_service.update_palette(0, False)
            try:
                self.LoadLastSetting()
            except Exception as e:
                print(e)

        else:
            self.point_list = self.point_list[:3]
            self.coord_input.InitFirstElementInput(
                AllplanIFW.InputStringConvert("Total input point is 3. Halfen type will be Rectangle"))
            self.geometry = "Rectangle"
            self.palette_service.close_palette()
            self.show_palette("PunchingShear")
            try:
                self.LoadLastSetting()
            except Exception as e:
                print(e)

    def modify_element_property(self, page, name, value):
        """
        Modify property of element
        """
        update_palette = self.palette_service.modify_element_property(page, name, value)

        # Update palette
        if update_palette:
            self.palette_service.update_palette(0, False)

    def draw_preview(self):
        if self.point_list == []:
            return
        # Symbols
        doc = self.coord_input.GetInputViewDocument()
        com_prop = AllplanBaseElements.CommonProperties()
        Symbol3DProp = AllplanBasisElements.Symbol3DProperties()
        Symbol3DProp.SymbolID = 4
        Symbol3DProp.Width = 20
        Symbol3DProp.Height = 20
        # List
        model_ele_list = []
        for point in self.point_list[:3]:
            model_ele_list += [AllplanBasisElements.Symbol3DElement(com_prop, Symbol3DProp, point)]
        AllplanBaseElements.DrawElementPreview(doc, AllplanGeo.Matrix3D(), model_ele_list, 0, None)

    def Draw_PSS(self, draw=True):
        doc = self.coord_input.GetInputViewDocument()
        # Get object
        try:
            Pss = Creator.PunchingShear_Creator(self, self.point_list, self.geometry)
            if Pss.error:
                return
            Pss_object = Pss.create()
            matrix = Pss.Get_matrix3D()
        except Exception as e:
            print(e)
            return
        # Draw Object
        if draw:
            try:
                AllplanBaseElements.CreateElements(doc, matrix, Pss_object, [], None)
            except Exception as e:
                print(e)
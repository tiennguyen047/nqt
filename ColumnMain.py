import os
import sys
import json

os.chdir(os.path.dirname(__file__))

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

import ColumnPoints as Points
from RebarColumn import COLUMNREBAR
from ColumnSection_Dung import SECTION_DUNG
from ColumnSection_Cat import SECTION_CAT

from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename

__userpath__    = AllplanSettings.AllplanPaths.GetUsrPath()
__currentpath__ = os.path.dirname(__file__)
last_setting    = "Column_Last_Setting.json"

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
        #input parameters
        self.coord_input        = coord_input
        self.doc                = self.coord_input.GetInputViewDocument()
        self.pyp_path           = pyp_path
        self.str_table_service  = str_table_service
        self.model_ele_list     = None
        self.build_ele_service  = BuildingElementService()
        self.palette_service    = None
        self.preview            = False
        #default parameters
        self.section_point      = False
        self.sel_column         = None
        self.sel_point          = None
        self.second_esc         = False
        self.current_pos        = AllplanReinf.ReinforcementUtil.GetNextBarPositionNumber(self.doc)
        #filter for columns
        type_query = AllplanIFW.QueryTypeID(AllplanElementAdapter.Column_TypeUUID )
        sel_query = AllplanIFW.SelectionQuery(type_query)
        self.element_filter = AllplanIFW.ElementSelectFilterSetting(sel_query, True)
        self.ShowPalatte("ColumnReinforcement.pal")
        try:
            self.LoadLastSetting()
        except:
            pass

    def GetSettingData(self):
        """ get current setting data """
        data = {}
        #general
        data['Column_Name']             = self.build_ele.Column_Name.value
        data['Concr_Cover']             = self.build_ele.Concr_Cover.value
        data['Concr_Grade']             = self.build_ele.Concr_Grade.value
        data['Slab_Above']              = self.build_ele.Slab_Above.value
        data['Create_Section']          = self.build_ele.Create_Section.value
        data['Create_Cross_Section'] 	= self.build_ele.Create_Cross_Section.value
        #main rebar
        data['Main_Diameter']           = self.build_ele.Main_Diameter.value
        data['Main_Crank']              = self.build_ele.Main_Crank.value
        data['Main_Crank_Distance']     = self.build_ele.Main_Crank_Distance.value
        data['Main_Starter']            = self.build_ele.Main_Starter.value
        #additional X rebar
        data['Add_X_Number']            = self.build_ele.Add_X_Number.value
        data['Add_X_Diameter']          = self.build_ele.Add_X_Diameter.value
        data['AddX_Crank']              = self.build_ele.AddX_Crank.value
        data['AddX_Crank_Distance']     = self.build_ele.AddX_Crank_Distance.value
        data['AddX_Starter']            = self.build_ele.AddX_Starter.value
        #additional Y rebar
        data['Add_Y_Number']            = self.build_ele.Add_Y_Number.value
        data['Add_Y_Diameter']          = self.build_ele.Add_Y_Diameter.value
        data['AddY_Crank']              = self.build_ele.AddY_Crank.value
        data['AddY_Crank_Distance']     = self.build_ele.AddY_Crank_Distance.value
        data['AddY_Starter']            = self.build_ele.AddY_Starter.value
        #stirrup
        data['Main_Stirrup_Diameter']   = self.build_ele.Main_Stirrup_Diameter.value
        data['Main_Stirrup_Spacing']    = self.build_ele.Main_Stirrup_Spacing.value
        data['Hook_Length']             = self.build_ele.Hook_Length.value
        data['Hook_Angle']              = self.build_ele.Hook_Angle.value
        data['Add_Stirrup_Top']         = self.build_ele.Add_Stirrup_Top.value
        data['Add_Stirrup_Top_Length']  = self.build_ele.Add_Stirrup_Top_Length.value
        data['Add_Stirrup_Top_Spacing'] = self.build_ele.Add_Stirrup_Top_Spacing.value
        data['Add_Stirrup_Bot']         = self.build_ele.Add_Stirrup_Bot.value
        data['Add_Stirrup_Bot_Length']  = self.build_ele.Add_Stirrup_Bot_Length.value
        data['Add_Stirrup_Bot_Spacing'] = self.build_ele.Add_Stirrup_Bot_Spacing.value
        data['Scale']                   = self.build_ele.Scale.value
        data['Min_Main_Diameter']       = self.build_ele.Min_Main_Diameter.value
        data['Min_Stirrup_Diameter']    = self.build_ele.Min_Stirrup_Diameter.value
        data['Max_Stirrup_Spacing']     = self.build_ele.Max_Stirrup_Spacing.value
        return data

    def LoadSettingData(self, data):
        """ load from setting data """
        #general
        self.build_ele.Column_Name.value                = data['Column_Name']
        self.build_ele.Concr_Cover.value                = data['Concr_Cover']
        self.build_ele.Concr_Grade.value                = data['Concr_Grade']
        self.build_ele.Slab_Above.value                 = data['Slab_Above']
        self.build_ele.Create_Section.value             = data['Create_Section']
        self.build_ele.Create_Cross_Section.value    	= data['Create_Cross_Section']
        #main rebar
        self.build_ele.Main_Diameter.value              = data['Main_Diameter']
        self.build_ele.Main_Crank.value                 = data['Main_Crank']
        self.build_ele.Main_Crank_Distance.value        = data['Main_Crank_Distance']
        self.build_ele.Main_Starter.value               = data['Main_Starter']   
        #additional X rebar
        self.build_ele.Add_X_Number.value               = data['Add_X_Number']
        self.build_ele.Add_X_Diameter.value             = data['Add_X_Diameter']
        self.build_ele.AddX_Crank.value                 = data['AddX_Crank']
        self.build_ele.AddX_Crank_Distance.value        = data['AddX_Crank_Distance']
        self.build_ele.AddX_Starter.value               = data['AddX_Starter']
        #additional Y rebar
        self.build_ele.Add_Y_Number.value               = data['Add_Y_Number']
        self.build_ele.Add_Y_Diameter.value             = data['Add_Y_Diameter']
        self.build_ele.AddY_Crank.value                 = data['AddY_Crank']
        self.build_ele.AddY_Crank_Distance.value        = data['AddY_Crank_Distance']
        self.build_ele.AddY_Starter.value               = data['AddY_Starter']
        #stirrup
        self.build_ele.Main_Stirrup_Diameter.value      = data['Main_Stirrup_Diameter']
        self.build_ele.Main_Stirrup_Spacing.value       = data['Main_Stirrup_Spacing']
        self.build_ele.Hook_Length.value                = data['Hook_Length']
        self.build_ele.Hook_Angle.value                 = data['Hook_Angle']
        self.build_ele.Add_Stirrup_Top.value            = data['Add_Stirrup_Top']
        self.build_ele.Add_Stirrup_Top_Length.value     = data['Add_Stirrup_Top_Length']
        self.build_ele.Add_Stirrup_Top_Spacing.value    = data['Add_Stirrup_Top_Spacing']
        self.build_ele.Add_Stirrup_Bot.value            = data['Add_Stirrup_Bot']
        self.build_ele.Add_Stirrup_Bot_Length.value     = data['Add_Stirrup_Bot_Length']
        self.build_ele.Add_Stirrup_Bot_Spacing.value    = data['Add_Stirrup_Bot_Spacing']
        self.build_ele.Scale.value                      = data['Scale']
        self.build_ele.Min_Main_Diameter.value          = data['Min_Main_Diameter']
        self.build_ele.Min_Stirrup_Diameter.value       = data['Min_Stirrup_Diameter']
        self.build_ele.Max_Stirrup_Spacing.value        = data['Max_Stirrup_Spacing']

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
            self.palette_service.update_palette(0, True)

    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        # Section Point
        if self.section_point:
            input_point = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info).GetPoint()
            if self.coord_input.IsMouseMove(mouse_msg):
                return True
            elif isinstance(input_point, AllplanGeo.Point3D):
                self.sel_point = input_point
                self.DrawColumn(self.sel_column, draw=False, section=True)
                self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert("Select next column to create reinforcement"))
                self.sel_column = None
                self.section_point = None
            return True

        #select column element
        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, True, True, self.element_filter)
        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        ele = self.coord_input.GetSelectedElement()
        if (not ele):
            return True

        #get 3d geometry points
        try:
            geo_list = ele.GetGeometry().GetVertices()
        except:
            try:
                geo_list = ele.GetModelGeometry().GetVertices()
            except:
                return True

        #check geometry
        if len(geo_list) < 8:
            return True

        #create rebar
        self.sel_column = geo_list
        if len(Points.get_8_points_column(self.sel_column)) == 8:
            self.DrawColumn(self.sel_column)
            self.SaveLastSetting()

        return True

    def on_control_event(self, event_id):
        """ control event for save and load """
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

    def main_diameter_limit(self):
        """ Diameter main cannot smaller than 12
        """
        AllplanUtil.ShowMessageBox("Main Column Rebar Diameter Ømin = {} mm!".format(self.build_ele.Min_Main_Diameter.value), AllplanUtil.MB_OK)
        self.build_ele.Main_Diameter.value = self.build_ele.Min_Main_Diameter.value
        self.palette_service.update_palette(-1, False)

    def stirrup_diameter_limit(self):
        """ Diameter stirrup cannot smaller than main diameter divide 4
        """
        AllplanUtil.ShowMessageBox("Stirrup diamter Ømin = {} mm!".format(self.build_ele.Min_Stirrup_Diameter.value), AllplanUtil.MB_OK)
        self.build_ele.Main_Stirrup_Diameter.value = self.build_ele.Min_Stirrup_Diameter.value
        self.palette_service.update_palette(-1, False)

    def stirrup_spacing_limit(self):
        """ Spacing stirrup cannot greater than 12*main diameter or 200 mm
        """
        AllplanUtil.ShowMessageBox("Stirrup spacing cannot greater than {} mm".format(self.build_ele.Max_Stirrup_Spacing.value), AllplanUtil.MB_OK)
        self.build_ele.Main_Stirrup_Spacing.value = self.build_ele.Max_Stirrup_Spacing.value
        self.palette_service.update_palette(-1, False)

    def add_stirrup_spacing_limit(self, name):
        """ Spacing additional stirrup cannot greater than 0.6* main spacing
        """
        AllplanUtil.ShowMessageBox("Additional stirrup spacing cannot greater than 0.6*<Main Spacing>", AllplanUtil.MB_OK)
        if name=="Add_Stirrup_Top_Spacing":
            self.build_ele.Add_Stirrup_Top_Spacing.value = round(0.6*(self.build_ele.Main_Stirrup_Spacing.value), -1)
        else:
            self.build_ele.Add_Stirrup_Bot_Spacing.value = round(0.6*(self.build_ele.Main_Stirrup_Spacing.value), -1)
        self.palette_service.update_palette(-1, False)

    def modify_element_property(self, page, name, value):
        """
        Modify property of element
        """
        update_palette = self.palette_service.modify_element_property(page, name, value)
            
        # Check main diameter
        if (name == "Main_Diameter"):
            if float(value) < self.build_ele.Min_Main_Diameter.value:
                self.main_diameter_limit()

        # Check stirrup diameter
        if (name == "Main_Stirrup_Diameter"):
            if float(value) < self.build_ele.Min_Stirrup_Diameter.value:
                self.stirrup_diameter_limit()

        # Check stirrup spacing
        if (name == "Main_Stirrup_Spacing"):
            if float(value) > self.build_ele.Max_Stirrup_Spacing.value:
                self.stirrup_spacing_limit()

        # Check additional stirrup spacing
        if (name == "Add_Stirrup_Top_Spacing") or (name == "Add_Stirrup_Bot_Spacing"):
            if float(value) > 0.6*(self.build_ele.Main_Stirrup_Spacing.value):
                self.add_stirrup_spacing_limit(name)

        # Update palette
        if update_palette:
            self.palette_service.update_palette(-1, False)

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
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert("Select columns to create reinforcement"))

    def CreateSection(self):
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert("Select point for section or press <ESC>"))
        self.section_point = True

    def DrawColumn(self, column_points, draw=True, section=False):
        #create rebar
        column = COLUMNREBAR(self.doc, self.build_ele, column_points, self.current_pos)
        if not column.OnCheckError():
            reins = column.Reinforcement()
        else:
            return

        if not section:
            AllplanBaseElements.CreateElements(self.doc, AllplanGeo.Matrix3D(), reins, [], None)

        #create section
        if section:
            ele_list = AllplanElementAdapter.BaseElementAdapterList()
            try:
                #mat dung
                inc_top = self.build_ele.Add_Stirrup_Top.value
                inc_bot = self.build_ele.Add_Stirrup_Bot.value
                section = SECTION_DUNG(self.doc, self.build_ele, column_points, self.sel_point, 50, self.current_pos, inc_top, inc_bot)
                section_dung = section.CreateSection()
                dimensions = section.DimensionLines()
                elevations = section.ElevationPoints()
                AllplanBaseElements.CreateSectionsAndViews(self.doc, AllplanGeo.Matrix3D(), ele_list,
                                                       section_dung, self.coord_input.GetViewWorldProjection())
                AllplanBaseElements.CreateElements(self.doc, AllplanGeo.Matrix3D(), dimensions + elevations, [], None)
                if self.build_ele.Create_Cross_Section.value:
                	spacing = self.build_ele.Main_Stirrup_Spacing.value
                	height  = abs(column_points[0].GetDistance(column_points[4]))
                	width   = abs(column_points[3].GetDistance(column_points[0]))
	                #mat cat giua
	                section = SECTION_CAT(self.doc, self.build_ele, column_points,
	                                        self.sel_point + AllplanGeo.Point3D(1000,height/2-width/2,0), 50,
	                                        self.current_pos + 11, height/2-spacing/2, spacing)
	                section_cat = section.CreateSection()
	                AllplanBaseElements.CreateSectionsAndViews(self.doc, AllplanGeo.Matrix3D(), ele_list,
	                                               						section_cat, self.coord_input.GetViewWorldProjection())

	                #mat cat top
	                if self.build_ele.Add_Stirrup_Top.value:
	                	spacing = self.build_ele.Add_Stirrup_Bot_Spacing.value
		                section = SECTION_CAT(self.doc, self.build_ele, column_points,
		                                        self.sel_point + AllplanGeo.Point3D(1000,height-width/2,0), 50,
		                                        self.current_pos + 12, height-spacing, spacing)
		                section_cat = section.CreateSection()
		                AllplanBaseElements.CreateSectionsAndViews(self.doc, AllplanGeo.Matrix3D(), ele_list,
		                                               						section_cat, self.coord_input.GetViewWorldProjection())

	                #mat cat bottom
	                if self.build_ele.Add_Stirrup_Bot.value:
	                	spacing = self.build_ele.Add_Stirrup_Top_Spacing.value
		                section = SECTION_CAT(self.doc, self.build_ele, column_points,
		                                        self.sel_point + AllplanGeo.Point3D(1000,-width/2,0), 50,
		                                        self.current_pos + 13, 0, spacing)
		                section_cat = section.CreateSection()
		                AllplanBaseElements.CreateSectionsAndViews(self.doc, AllplanGeo.Matrix3D(), ele_list,
		                                               						section_cat, self.coord_input.GetViewWorldProjection())
  
            except Exception as e:
                print(e)


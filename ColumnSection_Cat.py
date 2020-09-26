# Importing Allplan Pythonpart module
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil

import ColumnPoints as Points
import ColumnSetting as Setting
# Importing Python default module
import math

class SECTION_CAT():
    def __init__(self, doc, build_ele, column_points, ref_point, offset, current_pos, bot_level=0, dis_level=0):
        self.doc           = doc
        self.build_ele     = build_ele
        self.column_points = column_points
        self.offset        = offset
        self.current_pos   = current_pos
        self.bot_level     = bot_level
        self.dis_level     = dis_level
        self.ref_point     = AllplanGeo.Point2D(ref_point)
        self.concr_grade_list = Setting.ConcreteGrade()
        self.length        = abs(column_points[1].GetDistance(column_points[0]))
        self.width         = abs(column_points[3].GetDistance(column_points[0]))
        self.height        = abs(column_points[0].GetDistance(column_points[4]))
        self.angle         = Points.get2dangle_fr_3d(column_points[0], column_points[1])
        self.base_point    = self.column_points[0]
        self.common_prop   = AllplanBaseElements.CommonProperties()
        self.common_prop.GetGlobalProperties()
        self.text_props           = AllplanBasisElements.TextProperties()
        self.text_props.Alignment = AllplanBasisElements.TextAlignment.eMiddleTop
        self.On_Parameter()
        self.On_analysis()

    def On_Parameter(self):
        self.column_name    = self.build_ele.Column_Name.value
        self.concr_cover    = self.build_ele.Concr_Cover.value
        self.concr_grade    = self.build_ele.Concr_Grade.value
        self.slab_thickness = self.build_ele.Slab_Above.value
        self.main_stt       = self.build_ele.Main_Starter.value
        self.addX_stt       = self.build_ele.AddX_Starter.value
        self.addY_stt       = self.build_ele.AddY_Starter.value
        self.max_stt        = max(self.main_stt, self.addX_stt, self.addY_stt)

    def CreateSection(self):
        """ Tạo mặt cắt
        """
        sect_ele = AllplanBasisElements.ViewSectionElement()
        sect_ele.SectionDefinitionData    = self.Sec_def_data(0)
        #sect_ele.TextElements             = [self.Sec_label()]
        sect_ele.GeneralSectionProperties = self.Sec_props()
        sect_ele.ReinforcementLabels      = self.Reinf_label()
        return [sect_ele]        

    def Label_prop_dimen(self):
        """ Creating the Label Properties
        """
        label_prop = AllplanReinf.ReinforcementLabelProperties()
        label_prop.ShowBarCount         = False
        label_prop.ShowBarDiameter      = True
        label_prop.ShowPositionAtEnd    = False
        label_prop.ShowBarDistance      = True
        return label_prop

    def Label_prop_fan(self):
        """ Creating the Label Properties
        """
        label_prop = AllplanReinf.ReinforcementLabelProperties()
        label_prop.ShowPositionAtEnd    = True
        label_prop.ShowBarDiameter      = True
        label_prop.ShowBarCount         = True
        label_prop.ShowBarDistance      = False
        label_prop.ShowBarPlace         = True
        return label_prop

    def Reinf_label_dimension(self, mark_no, x, y, text_props, vec_int=None):
        label_prop  = self.Label_prop_dimen()
        label       = AllplanReinf.ReinforcementLabel(AllplanReinf.Bar, AllplanReinf.LabelWithDimensionLine,
                                                    mark_no, label_prop,
                                                    Points.addxy_2d(self.label_point, x, y),
                                                    AllplanGeo.Angle())
        if vec_int:
            label.SetVisibleBars(vec_int)
        else:
            label.ShowAllBars(True)
        label.SetTextProperties(text_props)
        return label

    def Reinf_label_pointer(self, mark_no, x, y, show_pos_at_end=False):
        label_prop = self.Label_prop_fan()
        if show_pos_at_end:
            label_prop.ShowPositionAtEnd = True

        label = AllplanReinf.ReinforcementLabel(AllplanReinf.Bar, AllplanReinf.LabelWithPointer,
                                                mark_no, label_prop,
                                                Points.addxy_2d(self.label_point, x, y),
                                                AllplanGeo.Angle())
        label.SetTextProperties(self.text_props)
        return label

    def Reinf_label(self):
        vec_int = AllplanUtil.VecIntList()
        vec_int.append(0)
        labels      = AllplanReinf.ReinforcementLabelList()

        #main stirrup
        labels.append(self.Reinf_label_pointer(self.current_pos, self.length/2, self.width + 300, vec_int))
        #top stirrup
        #labels.append(self.Reinf_label_dimension(self.current_pos+12, self.width + 300, self.height - 250, self.text_props, vec_int))
        #bottom stirrup
        #labels.append(self.Reinf_label_dimension(self.current_pos+13, self.width + 300, 250, self.text_props, vec_int))

        return labels

    def Sec_label(self):
        text_prop = AllplanBasisElements.TextProperties()
        text_prop.Alignment = AllplanBasisElements.TextAlignment.eMiddleMiddle
        text = "%U{" + "Stütze {}".format(self.column_name) + "%U}" + "\nb/h={}/{}cm, {}, B000A\nBetondeckung: Cv={} cm\nM 1:50"\
                        .format(int(round(self.length/10,0)), int(round(self.width/10,0)),
                                    self.concr_grade_list[int(self.concr_grade)], self.concr_cover)
        sec_label = AllplanBasisElements.TextElement(self.common_prop, text_prop,
                                                      text,
                                                      self.ref_point + AllplanGeo.Point2D(\
                                                      self.length/2, self.width + 1500))
        return sec_label

    def On_analysis(self):
        self.place_points = self.base_point
        angel1 = AllplanGeo.Vector2D(self.place_points.X, self.place_points.Y).GetAngle()
        angle  = (self.angle.GetDeg() - angel1.GetDeg())*math.pi/180
        delta  = Points.get2d_fr_3d(self.place_points).GetDistance(AllplanGeo.Point2D())
        self.delta = math.cos(angle)*delta
        self.moved_point = self.ref_point - AllplanGeo.Point2D(self.base_point) + AllplanGeo.Point2D(self.length, 0)
        self.label_point = Points.addy_2d(self.ref_point - self.moved_point, 0) + AllplanGeo.Point2D(500,0)

    def Sec_props(self):
        """ Creating the Section Properties
        """
        sec_prop = AllplanBasisElements.SectionGeneralProperties(True)
        sec_prop.Status           = AllplanBasisElements.SectionGeneralProperties.State.Hidden
        sec_prop.ShowSectionBody  = True
        sec_prop.FormatProperties = self.Sec_format_prop()
        sec_prop.FilterProperties = self.Sec_filter_prop()
        sec_prop.LabelingProperties = self.Sec_label_prop()
        sec_prop.PlacementPoint   = self.moved_point
        sec_prop.PlacementAngle   = 0
        return sec_prop

    def DimensionLines(self):
        dimen_lines = []
        dim_prop = AllplanBasisElements.DimensionProperties(self.doc, AllplanBasisElements.Dimensioning.eDimensionLine)

        # Dimensioning width
        dim_points = AllplanGeo.Point3DList()
        dim_points.append(AllplanGeo.Point3D(self.ref_point))
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(self.length,0,0))    
        dim_line = AllplanBasisElements.DimensionLineElement(dim_points, AllplanGeo.Vector2D(0, -400), AllplanGeo.Vector2D(1, 0), dim_prop)
        dim_line.SetCommonProperties(self.common_prop)
        dimen_lines.append(dim_line)

        # Dimensioning height
        dim_points = AllplanGeo.Point3DList()
        dim_points.append(AllplanGeo.Point3D(self.ref_point))
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(0,self.height,0))    
        dim_line = AllplanBasisElements.DimensionLineElement(dim_points, AllplanGeo.Vector2D(-300, 0), AllplanGeo.Vector2D(0, 1), dim_prop)
        dim_line.SetCommonProperties(self.common_prop)
        dimen_lines.append(dim_line)

        # Dimensioning Main Starter
        dim_points = AllplanGeo.Point3DList()
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(0,self.height + self.slab_thickness,0))
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(0,self.height + self.slab_thickness + self.main_stt,0))    
        dim_line = AllplanBasisElements.DimensionLineElement(dim_points, AllplanGeo.Vector2D(-300, 0), AllplanGeo.Vector2D(0, 1), dim_prop)
        dim_line.SetCommonProperties(self.common_prop)
        dimen_lines.append(dim_line)

        # Dimensioning AddX Starter
        dim_points = AllplanGeo.Point3DList()
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(0,self.height + self.slab_thickness,0))
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(0,self.height + self.slab_thickness + self.addX_stt,0))    
        dim_line = AllplanBasisElements.DimensionLineElement(dim_points, AllplanGeo.Vector2D(self.length + 300, 0), AllplanGeo.Vector2D(0, 1), dim_prop)
        dim_line.SetCommonProperties(self.common_prop)
        dimen_lines.append(dim_line)

        # Dimensioning AddX Starter
        dim_points = AllplanGeo.Point3DList()
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(0,self.height + self.slab_thickness,0))
        dim_points.append(AllplanGeo.Point3D(self.ref_point) + AllplanGeo.Point3D(0,self.height + self.slab_thickness + self.addY_stt,0))    
        dim_line = AllplanBasisElements.DimensionLineElement(dim_points, AllplanGeo.Vector2D(self.length + 600, 0), AllplanGeo.Vector2D(0, 1), dim_prop)
        dim_line.SetCommonProperties(self.common_prop)
        if self.addX_stt != self.addY_stt:
            dimen_lines.append(dim_line)

        return dimen_lines

    def ElevationPoints(self):
        input_point = self.ref_point
        # Properties
        elevation_prop = AllplanBasisElements.DimensionProperties(self.doc, AllplanBasisElements.Dimensioning.eElevation)
        # Elevation 1
        elevation = AllplanGeo.Point3DList()
        elevation.append(AllplanGeo.Point3D(input_point))
        elevation.append(AllplanGeo.Point3D(input_point))
        elevation.append(AllplanGeo.Point3D(input_point) + AllplanGeo.Point3D(0, self.height, 0))
        elevation_x1 = AllplanBasisElements.ElevationElement(elevation, AllplanGeo.Vector2D(-600, 0), AllplanGeo.Vector2D(0, 1), elevation_prop)
        
        return [elevation_x1]

    def Sec_format_prop(self):
        """ Creating the Section Format Properties
        """
        sec_format_prop = AllplanBasisElements.SectionGeneralProperties(True).FormatProperties
        sec_format_prop.IsEliminationOn  = False
        sec_format_prop.EliminationAngle = 22
        return sec_format_prop

    def Sec_filter_prop(self):
        """ Creating the Section Filter Properties
        """
        sec_filter_prop = AllplanBasisElements.SectionGeneralProperties(True).FilterProperties
        sec_filter_prop.DrawingFilesProperties = self.Sec_draw_files_prop()
        return sec_filter_prop

    def Sec_draw_files_prop(self):
        """ Creating the Drawing Files Properties
        """
        sec_draw_files_prop = AllplanBasisElements.SectionDrawingFilesProperties()
        sec_draw_files_prop.DrawingNumbers = self.Drawing_file_number()
        return sec_draw_files_prop

    def Drawing_file_number(self):
        """ Creating the Drawing Files Number
        """
        drawing_file_number = AllplanUtil.VecIntList()
        drawing_file_number.append(AllplanBaseElements.DrawingFileService.GetActiveFileNumber())
        return drawing_file_number

    def Sec_label_prop(self):
        """ Creating the Section Label Properties
        """
        sec_label_prop = AllplanBasisElements.SectionGeneralProperties(True).LabelingProperties
        sec_label_prop.HeadingOn = False
        return sec_label_prop

    def Sec_def_data(self, distance=0):
        section_def_data = AllplanBasisElements.SectionDefinitionData()
        section_def_data.ClippingPath = self.Sec_path()
        section_def_data.DefinitionProperties = self.Sec_def_prop()
        section_def_data.SectionBody = AllplanGeo.Polyhedron3D.CreateCuboid(
                                            AllplanGeo.Point3D(0, -1000, 0),
                                            AllplanGeo.Point3D(1000, 0, 1000))
        section_def_data.DirectionVector = AllplanGeo.Vector3D(self.column_points[4], self.column_points[0])

        return section_def_data

    def Sec_def_prop(self):
        """ Creating the Section Definition Properties
        """
        section_def_prop = AllplanBasisElements.SectionDefinitionProperties()
        section_def_prop.ClippingPathProperties = self.Clip_prop()
        return section_def_prop

    def Clip_prop(self):
        """ Creating the Clipping Path Properties
        """
        clip_prop = AllplanBasisElements.ClippingPathProperties()
        clip_prop.SectionIdentifier = str(1)
        clip_prop.IsHeightFromElementOn = False
        clip_prop.BottomLevel = self.base_point.Z - self.offset + self.bot_level
        clip_prop.TopLevel = self.base_point.Z + self.offset + self.bot_level + self.dis_level
        return clip_prop

    def Sec_path(self):
        offset = self.offset
        width  = self.width      
        length = self.length
        section_path = AllplanGeo.Polyline2D()
        section_path += AllplanGeo.Point2D(-offset, -offset)
        section_path += AllplanGeo.Point2D(length + offset, -offset)
        section_path += AllplanGeo.Point2D(length + offset, width + offset)
        section_path += AllplanGeo.Point2D(-offset, width + offset)
        section_path += AllplanGeo.Point2D(-offset, -offset)
        section_path = AllplanGeo.Move(section_path, 
                            AllplanGeo.Vector2D(self.place_points.Values()[0], self.place_points.Values()[1]))
        section_path = AllplanGeo.Rotate(section_path,
                            AllplanGeo.Point2D(self.place_points.Values()[0], self.place_points.Values()[1]), 
                            self.angle)
        return section_path



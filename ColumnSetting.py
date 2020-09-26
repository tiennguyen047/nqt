from enum import Enum
import configparser


def DiameterList():
    return ["6 mm", "8 mm", "10 mm", "12 mm", "14 mm", "16 mm", "20 mm", "25 mm", "28 mm", "32 mm"]

def ConcreteGrade():
    return ["C12/15", "C16/20", "C20/25", "C25/30", "C30/37", "C35/45", "C40/50", "C45/55", "C50/60",
                                   "C55/67", "C60/75", "C70/85", "C80/95", "C90/105"]

def ConcreteCover():
    return ["25 mm", "30 mm", "35 mm", "40 mm", "45 mm", "50 mm"]

#text language
parser   = configparser.SafeConfigParser()
parser.read("language.ini", encoding='utf-8')
language = parser.get("Default", "language")
#main
Text_panelcolumn            = parser.get(language, "panelcolumn")
Text_selectcolumn           = parser.get(language, "selectcolumn")
Text_selectcolumnabove      = parser.get(language, "selectcolumnabove")
Text_keyfail                = parser.get(language, "keyfail")
Text_keysuccess             = parser.get(language, "keysuccess")
Text_nokey                  = parser.get(language, "nokey")
Text_keyexpired             = parser.get(language, "keyexpired")
#gui
Text_title                  = parser.get(language, "title")
Text_rebar                  = parser.get(language, "rebar")
Text_license                = parser.get(language, "license")
#layout box sizer
Text_general                = parser.get(language, "general")
Text_mainrebar              = parser.get(language, "mainrebar")
Text_additionalx            = parser.get(language, "additionalx")
Text_additionaly            = parser.get(language, "additionaly")
Text_mainstirrup            = parser.get(language, "mainstirrup")
Text_addstirruptop          = parser.get(language, "addstirruptop")
Text_addstirrupbot          = parser.get(language, "addstirrupbot")
Text_crankbox               = parser.get(language, "crankbox")
#static text
Text_concrcover             = parser.get(language, "concrcover")
Text_concrgrade             = parser.get(language, "concrgrade")
Text_diameter               = parser.get(language, "diameter")
Text_starter                = parser.get(language, "starter")
Text_number                 = parser.get(language, "number")
Text_spacing                = parser.get(language, "spacing")
Text_hookangle              = parser.get(language, "hookangle")
Text_hooklength             = parser.get(language, "hooklength")
Text_placement              = parser.get(language, "placement")
Text_included               = parser.get(language, "included")
Text_crankincluded          = parser.get(language, "crankincluded")
Text_cranklength            = parser.get(language, "cranklength")

#check rebars
Text_minmainrebar           = parser.get(language, "minmainrebar")
Text_minstirrupdiameter     = parser.get(language, "minstirrupdiameter")
Text_maxstirrupspacing      = parser.get(language, "maxstirrupspacing")
Text_maxaddstirrupspacing   = parser.get(language, "maxaddstirrupspacing")

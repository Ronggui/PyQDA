# -*- coding: utf-8 -*-

'''
Copyright (c) 2013 Colin Curtain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Colin Curtain (ccbogel)
https://github.com/ccbogel/PyQDA
'''

import re


class CodeColors():
    """
     x11 colors as name hex and y or Null. y or Null is for too dark to code with
    100 colors are not marked as noshow=y. these 100 are shown in the color selector table
    Mostly original some have been lightened or darkened to improve text readability:
    blue, oldlace, green, lightyellow, linen, beige, whitesmoke
    """

    x11text = "LightPink,#FFB6C1,y;Pink,#FFC0CB,;Crimson,#DC143C,;LavenderBlush,#FFF0F5,;PaleVioletRed,#DB7093,;HotPink,#FF69B4,;DeepPink,#FF1493,;\
MediumVioletRed,#C71585,;Orchid,#DA70D6,;Thistle,#D8BFD8,;Plum,#DDA0DD,;Violet,#EE82EE,;Magenta,#FF00FF,y;Fuchsia,#FF00FF,;\
DarkMagenta,#8B008B,y;Purple,#800080,y;MediumOrchid,#BA55D3,;DarkViolet,#9400D3,;DarkOrchid,#9932CC,;Indigo,#4B0082,y;\
BlueViolet,#8A2BE2,;MediumPurple,#9370DB,;MediumSlateBlue,#7B68EE,;SlateBlue,#6A5ACD,;DarkSlateBlue,#483D8B,y;Lavender,#E6E6FA,;\
GhostWhite,#F8F8FF,y;Blue,#4040FF,;MediumBlue,#2F2FCD,;MidnightBlue,#191970,y;DarkBlue,#00008B,y;Navy,#000080,y;RoyalBlue,#4169E1,;\
CornflowerBlue,#6495ED,;LightSteelBlue,#B0C4DE,;LightSlateGray,#778899,;SlateGray,#708090,;DodgerBlue,#1E90FF,;AliceBlue,#F0F8FF,y;\
SteelBlue,#4682B4,;LightSkyBlue,#87CEFA,y;SkyBlue,#87CEEB,;DeepSkyBlue,#00BFFF,;LightBlue,#ADD8E6,;PowderBlue,#B0E0E6,;CadetBlue,#5F9EA0,;\
Azure,#E0EEEE,;LightCyan,#E0FFFF,;PaleTurquoise,#AFEEEE,;Cyan,#00FFFF,;Aqua,#00FFFF,y;DarkTurquoise,#00CED1,;DarkSlateGray,#2F4F4F,y;\
DarkCyan,#008B8B,;Teal,#008080,;MediumTurquoise,#48D1CC,;LightSeaGreen,#20B2AA,;Turquoise,#40E0D0,;Aquamarine,#7FFFD4,;MediumAquamarine,#66CDAA,;\
MediumSpringGreen,#00FA9A,;MintCream,#F5FFFA,y;SpringGreen,#00FF7F,;MediumSeaGreen,#3CB371,;SeaGreen,#2E8B57,;Honeydew,#F0FFF0,y;\
LightGreen,#90EE90,;PaleGreen,#98FB98,;DarkSeaGreen,#8FBC8F,;LimeGreen,#32CD32,;Lime,#00FF00,;ForestGreen,#228B22,;Green,#40F040,;\
DarkGreen,#006400,y;Chartreuse,#7FFF00,;LawnGreen,#7CFC00,y;GreenYellow,#ADFF2F,;DarkOliveGreen,#556B2F,y;YellowGreen,#9ACD32,;\
OliveDrab,#6B8E23,y;Beige,#F1F1DA,;LightGoldenrodYellow,#FAFAC2,;Ivory,#FFFFF0,y;LightYellow,#FFFFA0,;Yellow,#FFFF00,;Olive,#808000,y;\
DarkKhaki,#BDB76B,;LemonChiffon,#FFFACD,;PaleGoldenrod,#EEE8AA,y;Khaki,#F0E68C,;Gold,#FFD700,;Cornsilk,#FFF8DC,;Goldenrod,#DAA520,;\
DarkGoldenrod,#B8860B,;FloralWhite,#FFFAF0,y;OldLace,#FAF5E6,;Wheat,#F5DEB3,y;Moccasin,#FFE4B5,;Orange,#FFA500,;PapayaWhip,#FFEFD5,y;\
BlanchedAlmond,#FFEBCD,;NavajoWhite,#FFDEAD,;AntiqueWhite,#FAEBD7,;Tan,#D2B48C,;BurlyWood,#DEB887,y;Bisque,#FFE4C4,;DarkOrange,#FF8C00,;\
Linen,#F8E6E6,;Peru,#CD853F,y;PeachPuff,#FFDAB9,;SandyBrown,#F4A460,;Chocolate,#D2691E,;SaddleBrown,#8B4513,y;Seashell,#FFF5EE,y;\
Sienna,#A0522D,y;LightSalmon,#FFA07A,;Coral,#FF7F50,;OrangeRed,#FF4500,;DarkSalmon,#E9967A,;Tomato,#FF6347,;MistyRose,#FFE4E1,;\
Salmon,#FA8072,;Snow,#FFFAFA,y;LightCoral,#F08080,;RosyBrown,#BC8F8F,;IndianRed,#CD5C5C,;Red,#FF0F0F,;Brown,#A52A2A,y;FireBrick,#B22222,y;\
DarkRed,#8B0000,y;Maroon,#800000,y;White,#FFFFFF,y;WhiteSmoke,#F1F1F1,;Gainsboro,#DCDCDC,y;LightGrey,#D3D3D3,;Silver,#C0C0C0,;\
DarkGray,#A9A9A9,;Gray,#808080,;DimGray,#696969,y;Black,#000000,y"

    x11_strings = []
    x11_all = []
    x11_short = []

    def __init__(self):
        self.x11_strings = self.x11text.split(';')

        for c in self.x11_strings:
            temp = c.split(',')
            tempa = {"colname":temp[0].lower(), "hex":temp[1], "noshow":temp[2]}
            self.x11_all.append(tempa)
            if c[-1] != "y":
                temps = {"colname":temp[0].lower(), "hex":temp[1], "noshow":temp[2]}
                self.x11_short.append(temps)

    def getSelectorColor(self, x, y):
        """ Get selected color name from selected table widget cell. Used with the ColorSelector Dialog """

        return self.x11_short[x * 10 + y]

    # get color details from color name
    def getHexFromName(self,colname):
        """ Get colour hex value from the colour name.
        RQDA adds numbers after the colour name,
         so have to remove these first if using an RQDA database created in RQDA """

        if colname == None: colname = ""
        cname = re.sub("\d+", "", colname) #regex to remove digits, digits added to color names in original RQDA Db
        hexname = ""
        for c in self.x11_all:
            if cname.lower() == c['colname'].lower():
                hexname = c['hex']
        return hexname

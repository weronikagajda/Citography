# import sys
# import os
# import bpy
# import importlib

# blend_dir = os.path.dirname(bpy.data.filepath)
# if blend_dir not in sys.path:
#    sys.path.append(blend_dir)

from . import panels, operators

# importlib.reload(panels)
# importlib.reload(operators)
# importlib.reload(utilities)

bl_info = {
    "name" : "Citography - Beta",
    "author" : "Wero",
    "version" : (1, 9),
    "blender" : (3, 5, 1),
    "locoation" : "View3d > Tool",
    "description": "Extended Mapping Tool",
    "warning" : "",
    "wiki_url" : "",
    "catregory" : "3D View",   
}

#PANEL CITOGRAPHY - START 0.0
#   OPERATOR 0.1: clean the scene

#PANEL CITOGRAPHY - IMPORT 
#
#   PANEL: images
#   OPERATOR IMPORT IMAGES 1.0: 
#       OPERATOR 1.1: import one random image 
#       OPERATOR 1.2: distibute all images on a grid with choosen spacing
#       OPERATOR 1.3: RESIZE / ROTATE / *BEVEL/WRAP
#   
#   PANEL: geoimages
#   OPERATOR IMPORT 2.0: import geolocated images
#       OPERATOR 2.1: georeference
#
#   PANEL: CSV/GPX data
#   OPERATOR IMPORT 3: import csv/gps data
#       OPERATOR 1: import points
#       OPERATOR 2: make a path
    
def register():
    panels.register()
    operators.register()

def unregister():
    panels.unregister()
    operators.unregister()
    
if __name__ == "__main__":
    register()
    




from . import panels, operators

bl_info = {
    "name" : "Citography - Beta",
    "author" : "Wero",
    "version" : (1, 10),
    "blender" : (3, 5, 1),
    "locoation" : "View3d > Tool",
    "description": "Extended Mapping Tool",
    "warning" : "",
    "wiki_url" : "",
    "catregory" : "3D View",   
}
    
def register():
    panels.register()
    operators.register()

def unregister():
    panels.unregister()
    operators.unregister()
    
if __name__ == "__main__":
    register()
    

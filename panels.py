from bpy.types import Panel
from .operators import *
from .utilities import *


class Panel_PT_CitoStart(bpy.types.Panel):
    bl_label = "CITOGRAPHY - Start:"
    bl_idname = "C_PT_CitoPanelStart"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Citography"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        layout.operator("object.cleanthescene", text="Clean the scene")
        
# class Panel_PT_CitographyStart(Panel):
#     bl_label = "CITOGRAPHY - Start"
#     bl_idname = "C_PT_CitoStartPanel"  # Updated to follow convention
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = "Citography" 
#     bl_context = "objectmode"
    
#     def draw(self, context):
#         layout = self.layout
#         row = layout.row()
#         row.operator("object.simple_add_cube", icon= "X")  # Using the string ID directly
#         row = layout.row()
#         layout.label(text="* use BlenderGIS to georeference the scene")

# main panel - import
class Panel_PT_CitographyImport(Panel):
    bl_label = "CITOGRAPHY - Import:"
    bl_idname = "C_PT_CitoImportPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Citography" 
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

# main panel - explore
class Panel_PT_CitographyExplore(Panel):
    bl_label = "CITOGRAPHY - Explore:"
    bl_idname = "C_PT_CitoExplorePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Citography" 
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

# sub panel - import
class SubPanel_PT_Image(Panel):
    bl_label = "IMAGES:"
    bl_idname = "C_PT_CitoImagePanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Citography"
    bl_parent_id = "C_PT_CitoImportPanel"
    bl_options = {"DEFAULT_CLOSED"} 
    
    def draw(self, context):
        layout = self.layout
        
        scene = context.scene
        layout.prop(scene, "path1", text="Folder") 
        layout.separator(factor=2)

        row = layout.row()
        row.operator("object.add_random_image", icon= "IMAGE_RGB")  
        row = layout.row()
         # Split the row to place elements side by side
        split = row.split(factor=0.5, align=True)  # Adjust the 'factor' to allocate space for button and slider
        split.operator("object.images_grid", icon= "LIGHTPROBE_GRID", text="Grid")
        split.prop(scene, "spacing", text="Spacing", slider=True)
        row = layout.row()
        row.label(text="Select and:", icon="ARROW_LEFTRIGHT")
        row.operator("transform.resize")
        row = layout.row()
        row.label(text="Select and:", icon="EMPTY_ARROWS")
        row.operator("transform.rotate")

# sub panel - import
class  SubPanel_PT_Geoimages(Panel):
    bl_label = "GEO-LOC-IMAGES:"
    bl_idname = "C_PT_CitoGeoLocPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Citography"
    bl_parent_id = "C_PT_CitoImportPanel"  
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        
        scene = context.scene
        layout.prop(scene, "path2", text="Folder")
        layout.separator()
        row = layout.row()
        row.label(text= "WARNING! The scene has to be georeferenced!", icon= "ERROR")
        layout = self.layout
        layout.operator("object.geo_images_import", text=SelectFolderImages.bl_label)
        row = layout.row()
        row.label(text="Select and:", icon="SHADING_WIRE")
        row.operator("object.rotate_images_flat", text=TurnImageFlat.bl_label)
        row = layout.row()
        row.label(text="Select and:", icon="SHADING_WIRE")
        row.operator("object.rotate_same_z", text=TurnImagesZRotation.bl_label)

#sub panel - import
class SubPanel_PT_GPSData(Panel):
    bl_label = "GPS-LOC-DATA:"
    bl_idname = "C_PT_CitoStartPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Citography"
    bl_parent_id = "C_PT_CitoImportPanel"  
    bl_options = {"DEFAULT_CLOSED"} 
    
    def draw(self, context):
        layout = self.layout        
        scene = context.scene
        layout.prop(scene, "path3", text="File") 
        layout.separator()
        row = layout.row()
        row.operator(ImportCSVFile.bl_idname, text=ImportCSVFile.bl_label)

#sub panel - import
class SubPanel_PT_Explore2DMap(Panel):
    bl_label = "2D MAP"
    bl_idname = "C_PT_Cito2dmapPpanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Citography"
    bl_parent_id = "C_PT_CitoExplorePanel"  
    bl_options = {"DEFAULT_CLOSED"} 
    
    def draw(self, context):
        layout = self.layout
        obj = context.object 
        row = layout.row()

# # sub panel - import
class SubPanel_PT_Explore_3DMap(Panel):
    bl_label = "3D MAP"
    bl_idname = "C_PT_Cito3mapPpanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Citography"
    bl_parent_id = "C_PT_CitoExplorePanel"  
    bl_options = {"DEFAULT_CLOSED"} 
    
    def draw(self, context):
        layout = self.layout
        obj = context.object 
        row = layout.row()

def register():
    bpy.utils.register_class(Panel_PT_CitoStart)
    bpy.utils.register_class(Panel_PT_CitographyImport)
    bpy.utils.register_class(SubPanel_PT_Image)
    bpy.utils.register_class(SubPanel_PT_Geoimages)
    bpy.utils.register_class(SubPanel_PT_GPSData)
    bpy.utils.register_class(Panel_PT_CitographyExplore)
    bpy.utils.register_class(SubPanel_PT_Explore2DMap)
    bpy.utils.register_class(SubPanel_PT_Explore_3DMap)
    
def unregister():
    bpy.utils.unregister_class(Panel_PT_CitoStart)
    bpy.utils.unregister_class(Panel_PT_CitographyImport)
    bpy.utils.unregister_class(SubPanel_PT_Image)
    bpy.utils.unregister_class(SubPanel_PT_Geoimages)
    bpy.utils.unregister_class(SubPanel_PT_GPSData)
    bpy.utils.unregister_class(Panel_PT_CitographyExplore)
    bpy.utils.unregister_class(SubPanel_PT_Explore2DMap)
    bpy.utils.unregister_class(SubPanel_PT_Explore_3DMap)

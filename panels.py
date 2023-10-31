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
        layout.operator("object.cleanthescene", text="Clean the scene", icon= "X")

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
        row.prop(scene, "spacing", text="Spacing", slider=True)  
        row = layout.row()
        row.operator("object.images_grid", icon= "LIGHTPROBE_GRID", text="Grid")
        row = layout.row()
        row.operator("object.images_spheres", icon= "THREE_DOTS", text="Spheres")
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
        row.label(text="Select and:", icon="DOCUMENTS")
        row.operator("object.rotate_images_flat", text=TurnImageFlat.bl_label)
        row = layout.row()
        row.label(text="Select and:", icon="STICKY_UVS_DISABLE")
        row.operator("object.rotate_same_z", text=TurnImagesZRotation.bl_label)
        row = layout.row()
        row.label(text="Select and:", icon="SNAP_EDGE")
        row.operator("object.reset_to_original", text=ResetToOriginal.bl_label)

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
        row.operator(ImportGPXFile.bl_idname, text=ImportGPXFile.bl_label)
        row = layout.row()
        if hasattr(scene, "gpx_duration"):
            duration_text = f"GPX Duration: {scene.gpx_duration}"
            row.label(text=duration_text)
        row = layout.row()
        row.operator(ImportCSVFile.bl_idname, text=ImportCSVFile.bl_label)
        row = layout.row()
        if hasattr(scene, "csv_duration"):
            row.label(text=f"CSV Duration: {scene.csv_duration}")
        row = layout.row()
        row.operator(MakeVertextsToPath.bl_idname, icon="IPO_CONSTANT", text=MakeVertextsToPath.bl_label)
        row = layout.row()       
        split = row.split(factor=0.5, align=True)
        split.operator(MakeVertexToBezier.bl_idname, icon="IPO_BACK", text="Bezier Path")
        split.prop(scene, "curve_resolution_u", text="Resolution", slider=True)
        row = layout.row()

#sub panel - import
class SubPanel_PT_Explore2DMap(Panel):
    bl_label = "2D MAPPING"
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
        row.operator("view3d.set_camera_top_view", text="Top View Camera")
        row = layout.row()

# # sub panel - import
class SubPanel_PT_Explore3DMap(Panel):
    bl_label = "3D MAPPING"
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
        row.label(text="Select a Bezier Path:", icon="IPO_BACK")
        row = layout.row()
        row.operator("view3d.set_camera_animation_path", text="Add a Camera")
        row = layout.row()
        row.label(text="Select the Camera:", icon="CAMERA_DATA")
        row = layout.row()
        row.operator("view3d.animate_camera_along_path", text="Animation: Along the Path")

classes = [
    Panel_PT_CitoStart,
    Panel_PT_CitographyImport,
    SubPanel_PT_Image,
    SubPanel_PT_Geoimages,
    SubPanel_PT_GPSData,
    Panel_PT_CitographyExplore,
    SubPanel_PT_Explore2DMap,
    SubPanel_PT_Explore3DMap,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

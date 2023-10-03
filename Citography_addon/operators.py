import os
import math
import random
import pandas as pd #CHECK IF INSTALLED
import bpy
import bpy_extras.io_utils
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty
from PIL import Image #CHECK IF INSTALLED
from pyproj import Transformer #CHECK IF INSTALLED
from PIL.ExifTags import TAGS, GPSTAGS
from .utilities import *

IMAGE_SCALE = (8, 8, 8)
TRANSFORM_PIVOT_POINT = 'INDIVIDUAL_ORIGINS'
VALID_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')

class CleanTheScene(bpy.types.Operator):
    bl_idname = "object.cleanthescene"
    bl_label = " Clean the scene "
    
    def execute(self, context):
        print("Operator CleanTheScene is called!")
        try:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {e}")
        return {'FINISHED'}

# class SimpleAddCube(bpy.types.Operator):
#     bl_idname = "object.simple_add_cube"
#     bl_label = "Add Cube"
    
#     def execute(self, context):
#         bpy.ops.mesh.primitive_cube_add(size=2)
#         return {'FINISHED'}

class SelectFolderImages(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "some_data.select_source"  
    bl_label = "Import geolocated images"

    def execute(self, context):
        try:
            # Convert to absolute path
            folderpath = bpy.path.abspath(self.filepath)
            # Assign the folder path to context.scene.path1, path2, and path3
            context.scene.path1 = folderpath
            context.scene.path2 = folderpath
            context.scene.path3 = folderpath
            context.scene.path4 = folderpath
            print(folderpath)
        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {e}")

        return {'FINISHED'}
    
class AddRandomImage(Operator):
    bl_idname = "object.add_random_image"
    bl_label = "Random Image"
    
    def execute(self, context):
        path_for_images = bpy.path.abspath(context.scene.path1)  
        all_images = []  
        
        # Error handling for directory check and file retrieval
        if os.path.isdir(path_for_images):
            all_images = os.listdir(path_for_images)  
        else:
            self.report({'WARNING'}, f"The path {path_for_images} is not a valid directory.")
            return {'CANCELLED'}

        try:
            if all_images:
                random_image = random.choice(all_images)
                print(f"Adding a random image: {random_image}")
                enable_addon("io_import_images_as_planes")
                import_images_as_plane(os.path.join(path_for_images, random_image))
                if context.object:
                    context.object.scale = IMAGE_SCALE
            else:
                self.report({'WARNING'}, "No images found in the specified directories.")
        except Exception as e: 
            self.report({'ERROR'}, f"An error occurred: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class DistributeImagesGrid(Operator):
    bl_idname = "object.images_grid"
    bl_label = "Grid"

    def execute(self, context):
        path_for_images = bpy.path.abspath(context.scene.path1)
        
        try:
            if not os.path.isdir(path_for_images):
                self.report({'WARNING'}, f"The path {path_for_images} is not a valid directory.")
                return {'CANCELLED'}
            
            all_images = get_all_images(path_for_images)
            num_images = len(all_images)
            grid_size = int(math.sqrt(num_images))
            spacing = context.scene.spacing
            cursor_location = context.scene.cursor.location

            for i, image_path in enumerate(all_images):
                row = i // grid_size
                col = i % grid_size
                x = cursor_location.x + (col * spacing)
                y = cursor_location.y - (row * spacing)
                z = cursor_location.z
                
                import_images_as_plane(image_path, location=(x, y, z))
                
        except FileNotFoundError:
            self.report({'ERROR'}, f"Image file not found: {image_path}")
            return {'CANCELLED'}
        except Exception as e:  
            self.report({'ERROR'}, f"An error occurred: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}    
 
class ImportGeoImages(Operator):
    bl_idname = "object.geo_images_import"
    bl_label = "Import"

    VALID_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg'} 
    SRC_CRS = "EPSG:4326"
    DEST_CRS = "EPSG:3857"

    def handle_exif(self, img_path):
        image = Image.open(img_path)
        exif_data = image._getexif()
        if exif_data is not None:
            for (tag, value) in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'GPSInfo':
                    gps_data = {}
                    for t in value:
                        sub_tag_name = GPSTAGS.get(t, t)
                        gps_data[sub_tag_name] = value[t]
                    return gps_data
        return {}  # return an empty dict if no GPSInfo tag

    def convert_gps_data(self, gps_data, altitude):
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

        latitude = gps_data.get('GPSLatitude', [0, 0, 0])
        longitude = gps_data.get('GPSLongitude', [0, 0, 0])

        latitude = latitude[0] + latitude[1]/60 + latitude[2]/3600
        longitude = longitude[0] + longitude[1]/60 + longitude[2]/3600

        x, y = transformer.transform(longitude, latitude)

        # Convert altitude from feet to meters
        z = altitude #* 0.3048

        # Get the coordinates of the scene origin in the EPSG:3857 system
        scene_origin_crs_x = bpy.data.scenes["Scene"]["crs x"]
        scene_origin_crs_y = bpy.data.scenes["Scene"]["crs y"]

        # Calculate the position of the image in the scene
        position_in_scene_x = x - scene_origin_crs_x
        position_in_scene_y = y - scene_origin_crs_y
        position_in_scene_z = z

        return (position_in_scene_x, position_in_scene_y, position_in_scene_z)

    def import_image_as_plane(self, img_path, location, scale_factor=45):
        bpy.ops.import_image.to_plane(files=[{"name": img_path, "name": img_path}], directory=os.path.dirname(img_path))
        obj = bpy.context.selected_objects[0]
        obj.location = location

        # Additional code to rotate the image
        gps_data = self.handle_exif(img_path)
        orientation = gps_data.get('GPSImgDirection', 0)
        obj.rotation_euler = (math.radians(85), 0, math.radians(orientation))

        # Scale up the image by the scale factor
        obj.scale = (scale_factor, scale_factor, scale_factor)

    def execute(self, context):
        """Execute the operator: Import geotagged images and place them in the scene."""
        img_dir = bpy.path.abspath(context.scene.path2)
        img_dir = os.path.normpath(img_dir)
        
        for img_name in os.listdir(img_dir):
            img_path = os.path.join(img_dir, img_name)
            
            # Check for valid image extensions using a set
            _, ext = os.path.splitext(img_name)
            if ext.lower() in self.VALID_IMAGE_EXTENSIONS:
                gps_data = self.handle_exif(img_path)
                
                # Notify user and continue if no GPS data
                if not gps_data:
                    self.report({'WARNING'}, f"No GPS data for {img_name}. Skipping.")
                    continue

                altitude = gps_data.get('GPSAltitude', 0)
                transformed_coordinates = self.convert_gps_data(gps_data, altitude)
                self.import_image_as_plane(img_path, transformed_coordinates)

        return {'FINISHED'}



class TurnImageFlat(Operator):
    bl_idname = "object.rotate_images_flat"
    bl_label = "Flat rotation"

    def execute(self, context):
        context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        for obj in context.selected_objects:
            obj.rotation_euler[0] = 0
        return {'FINISHED'}
    
class TurnImagesZRotation(Operator):
    bl_idname = "object.rotate_same_z"
    bl_label = "Same z - rotation"

    def execute(self, context):
        context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        for obj in context.selected_objects:
            obj.rotation_euler[2] = 0
        return {'FINISHED'}

class ImportCSVFile(Operator):
    bl_idname = "some_data.csv_file"
    bl_label = "CSV - location data"

    @staticmethod
    def convert_gps_data(latitude, longitude, altitude):
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

        x, y = transformer.transform(longitude, latitude)

        # Convert altitude from feet to meters
        z = altitude  # * 0.3048

        # Retrieve the coordinates of the scene origin in the EPSG:3857 system
        scene_origin_crs_x = bpy.data.scenes["Scene"]["crs x"]
        scene_origin_crs_y = bpy.data.scenes["Scene"]["crs y"]

        # Calculate the position of the point in the scene
        position_in_scene_x = x - scene_origin_crs_x
        position_in_scene_y = y - scene_origin_crs_y
        position_in_scene_z = z

        return (position_in_scene_x, position_in_scene_y, position_in_scene_z)

    def execute(self, context):
        img_dir = bpy.path.abspath(context.scene.path3)  # convert to absolute path
        
        # Validate if the file exists
        if not os.path.exists(img_dir):
            self.report({'ERROR'}, f"File does not exist: {img_dir}")
            return {'CANCELLED'}
        
        try:
            data = pd.read_csv(img_dir)
        except Exception as e:
            self.report({'ERROR'}, f"Error reading CSV file: {str(e)}")
            return {'CANCELLED'}

        # Create new mesh and object
        new_mesh = bpy.data.meshes.new(name='data')
        new_object = bpy.data.objects.new('data_graph', new_mesh)

        # Link the object to the scene
        bpy.context.scene.collection.objects.link(new_object)
        bpy.context.view_layer.objects.active = new_object
        new_object.select_set(True)

        # Define lists for mesh data
        vertices = []

        # Create vertices from GPS data
        for _, row in data.iterrows():
            converted_coordinates = self.convert_gps_data(row['latitude'], row['longitude'], row['altitude'])
            vertices.append(converted_coordinates)

        # Update mesh with new data
        new_mesh.from_pydata(vertices, [], [])
        new_mesh.update()
        
        self.report({'INFO'}, f"Created mesh with {len(vertices)} vertices.")
    
        return {'FINISHED'}

# class DataPointsToCurve(Operator):
#     bl_idname = "object.datapoints_to_curve"
#     bl_label = "Points to Curve"

#     def execute(self, context):
#         return {'FINISHED'}
    
def register():
    bpy.utils.register_class(CleanTheScene)
    bpy.utils.register_class(AddRandomImage)
    bpy.utils.register_class(DistributeImagesGrid)
    bpy.utils.register_class(SelectFolderImages)
    bpy.utils.register_class(ImportGeoImages)
    #bpy.utils.register_class(SimpleAddCube)
    bpy.utils.register_class(TurnImageFlat)
    bpy.utils.register_class(TurnImagesZRotation)
    bpy.utils.register_class(ImportCSVFile)
    #bpy.utils.register_class(DataPointsToCurve)
    bpy.types.Scene.path1 = bpy.props.StringProperty(
        name="Path1",
        description="A filepath",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    bpy.types.Scene.path2 = bpy.props.StringProperty(
        name="Path2",
        description="A filepath",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    bpy.types.Scene.path3 = bpy.props.StringProperty(
        name="Path3",
        description="A filepath",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    bpy.types.Scene.spacing = bpy.props.FloatProperty(
        name="Spacing",
        description="Space between images in the grid",
        default=2.0,
        min=0.0,
        max=10.0
    )

       
def unregister():
    bpy.utils.unregister_class(CleanTheScene)
    bpy.utils.unregister_class(AddRandomImage)
    bpy.utils.unregister_class(DistributeImagesGrid)
    bpy.utils.unregister_class(SelectFolderImages)
    bpy.utils.unregister_class(ImportGeoImages)
    #bpy.utils.unregister_class(SimpleAddCube)
    bpy.utils.unregister_class(TurnImageFlat)
    bpy.utils.unregister_class(TurnImagesZRotation)
    bpy.utils.register_class(ImportCSVFile)
    del bpy.types.Scene.path1
    del bpy.types.Scene.path2
    del bpy.types.Scene.path3
    del bpy.types.Scene.spacing
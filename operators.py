import os
import math
import random
import pandas as pd #CHECK IF INSTALLED
import bpy
import bmesh
import bpy_extras.io_utils
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty
from PIL import Image #CHECK IF INSTALLED
from pyproj import Transformer #CHECK IF INSTALLED
from PIL.ExifTags import TAGS, GPSTAGS
from .utilities import *
import xml.etree.ElementTree as ET #for strava files
from datetime import datetime

IMAGE_SCALE = (8, 8, 8)
TRANSFORM_PIVOT_POINT = 'INDIVIDUAL_ORIGINS'
VALID_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.hdr')

# Properties to register
properties = {
    "path1": bpy.props.StringProperty(
        name="Path1",
        description="A filepath",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    ),
    "path2": bpy.props.StringProperty(
        name="Path2",
        description="A filepath",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    ),
    "path3": bpy.props.StringProperty(
        name="Path3",
        description="A filepath",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    ),
    "spacing": bpy.props.FloatProperty(
        name="Spacing",
        description="Space between images in the grid",
        default=2.0,
        min=0.0,
        max=10.0
    ),
    "curve_resolution_u": bpy.props.IntProperty(
        name="Resolution",
        description="Bezier curve resolution u",
        default=4,
        min=0,
        max=30
    ),
    "gpx_duration": bpy.props.StringProperty(
        name="GPX_Duration",
        description= "Duration extracted from GPX file",
        default=""
    ),
    "csv_duration": bpy.props.StringProperty(
        name="CSV Duration",
        description="Duration extracted from CSV file",
        default=""
    )
}

class CleanTheScene(bpy.types.Operator):
    bl_idname = "object.cleanthescene"
    bl_label = " Clean the scene "
    
    def execute(self, context):
        print("Operator CleanTheScene is called!")
        try:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
            # Push an undo step
            bpy.ops.ed.undo_push(message="Delete All Objects")
            
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
    
class DistributeImagesSphere(Operator):
    bl_idname = "object.images_spheres"
    bl_label = "Spheres"

    def execute(self, context):
        path_for_images = bpy.path.abspath(context.scene.path1)
        
        try:
            if not os.path.isdir(path_for_images):
                self.report({'WARNING'}, f"The path {path_for_images} is not a valid directory.")
                return {'CANCELLED'}
            
            all_images = get_all_images(path_for_images)
            spacing = context.scene.spacing
            cursor_location = context.scene.cursor.location

            for image_path in all_images:
                # Load image into Blender
                image = bpy.data.images.load(image_path)  

                # 1. Create the Sphere
                x = cursor_location.x + spacing
                y = cursor_location.y 
                z = cursor_location.z
                bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(x, y, z))
                sphere = bpy.context.active_object

                # 2. Create a New Material and assign it to the Sphere
                material = bpy.data.materials.new(name="Sphere_Material")
                sphere.data.materials.append(material)

                # 4. Set up the Shader Nodes
                material.use_nodes = True
                nodes = material.node_tree.nodes

                # Clear default nodes
                for node in nodes:
                    nodes.remove(node)

                # Add Shader to RGB node
                shader_to_rgb = nodes.new(type='ShaderNodeShaderToRGB')
                shader_to_rgb.location = (0,0)

                # Add an Emission shader node
                emission = nodes.new(type='ShaderNodeEmission')
                emission.location = (200,0)

                # Add a Material Output node and connect the Emission shader to it
                material_output = nodes.new(type='ShaderNodeOutputMaterial')   
                material_output.location = (400,0)

                # Add an Image Texture node and set its image to the loaded HDRI
                image_texture = nodes.new(type='ShaderNodeTexImage')
                image_texture.image = image
                image_texture.location = (-200,0)

                # Connect the nodes together
                noodle1 = material.node_tree.links.new
                noodle1(shader_to_rgb.outputs["Color"], emission.inputs["Color"])
                noodle1(emission.outputs["Emission"], material_output.inputs["Surface"])
                noodle1(image_texture.outputs["Color"], shader_to_rgb.inputs[0]) 

                cursor_location.x += spacing 
                
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

        # Save original position and rotation
        obj["original_location"] = obj.location[:]
        obj["original_rotation"] = obj.rotation_euler[:]

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
    bl_label = "Same Z axis rotation"

    def execute(self, context):
        context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        for obj in context.selected_objects:
            obj.rotation_euler[2] = 0
        return {'FINISHED'}
    
class ResetToOriginal(Operator):
    bl_idname = "object.reset_to_original"
    bl_label = "Reset to original"

    def execute(self, context):
        for obj in context.selected_objects:
            if "original_location" in obj.keys() and "original_rotation" in obj.keys():
                obj.location = obj["original_location"]
                obj.rotation_euler = obj["original_rotation"]
            else:
                self.report({'WARNING'}, f"No original data saved for {obj.name}. Skipping.")
        return {'FINISHED'}

class ImportCSVFile(Operator):
    bl_idname = "some_data.csv_file"
    bl_label = "CSV - location data"

    @staticmethod
    def convert_gps_data(latitude, longitude, altitude):
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

        x, y = transformer.transform(longitude, latitude)

        # Convert altitude from feet to meters
        z = altitude  * 0.3048

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

#importing strava
class ImportGPXFile(Operator):
    bl_idname = "some_data.gpx_file"
    bl_label = "GPX - location data"

    @staticmethod
    def convert_gps_data(latitude, longitude, altitude):
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

        x, y = transformer.transform(longitude, latitude)
        z = altitude  # GPX typically uses meters for altitude, but if this changes you can adjust

        scene_origin_crs_x = bpy.data.scenes["Scene"]["crs x"]
        scene_origin_crs_y = bpy.data.scenes["Scene"]["crs y"]

        position_in_scene_x = x - scene_origin_crs_x
        position_in_scene_y = y - scene_origin_crs_y
        position_in_scene_z = z

        return (position_in_scene_x, position_in_scene_y, position_in_scene_z)

    def execute(self, context):
        gpx_dir = bpy.path.abspath(context.scene.path3)
        
        if not os.path.exists(gpx_dir):
            self.report({'ERROR'}, f"File does not exist: {gpx_dir}")
            return {'CANCELLED'}

        tree = ET.parse(gpx_dir)
        root = tree.getroot()

        # Extract start and end times (if available)
        start_time_element = root.find(".//{http://www.topografix.com/GPX/1/1}trkpt/{http://www.topografix.com/GPX/1/1}time")
        if start_time_element is not None:
            start_time = start_time_element.text
        else:
            self.report({'WARNING'}, "No start time found in GPX data")
            start_time = None

        end_time_elements = list(root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt/{http://www.topografix.com/GPX/1/1}time"))
        if end_time_elements:
            end_time = end_time_elements[-1].text
        else:
            self.report({'WARNING'}, "No end time found in GPX data")
            end_time = None

        # Optional: calculate and format the duration
        if start_time and end_time:
            start_datetime = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end_datetime = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            duration = end_datetime - start_datetime
            formatted_duration = format_duration(duration)
            context.scene.gpx_duration = formatted_duration

        # Create new mesh and object
        new_mesh = bpy.data.meshes.new(name='data')
        new_object = bpy.data.objects.new('data_graph', new_mesh)

        bpy.context.scene.collection.objects.link(new_object)
        bpy.context.view_layer.objects.active = new_object
        new_object.select_set(True)

        vertices = []

        # Extract and convert trackpoints from GPX data
        for trkpt in root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt"):
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            ele = float(trkpt.find("{http://www.topografix.com/GPX/1/1}ele").text)
            
            converted_coordinates = self.convert_gps_data(lat, lon, ele)
            vertices.append(converted_coordinates)

        new_mesh.from_pydata(vertices, [], [])
        new_mesh.update()
        
        self.report({'INFO'}, f"Created mesh with {len(vertices)} vertices.")
        
        return {'FINISHED'}
       
class MakeVertextsToPath(Operator):
    bl_idname = "object.vertex_to_path"
    bl_label = " Polyline "
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        try: 
            # Assume that the desired object is currently selected
            obj = bpy.context.active_object

            # Store the initial mode
            initial_mode = bpy.context.object.mode

            # Ensure you are in Edit mode
            if initial_mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')

            # Get the mesh and BMesh
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            # Get the selected vertices
            selected_verts = [v for v in bm.verts if v.select]

            # Prepare a list to store global coordinates
            coords = [obj.matrix_world @ v.co for v in selected_verts]

            # Switch back to initial mode before creating the curve to avoid context issues
            bpy.ops.object.mode_set(mode=initial_mode)

            # Create a new curve
            curve_data = bpy.data.curves.new(obj.name + '_curve', type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.resolution_u = 10  # Increasing for smoother curves

            # Create a new object with the curve
            curve_object = bpy.data.objects.new(obj.name + '_curve', curve_data)
            curve_object.location = obj.location
            bpy.context.collection.objects.link(curve_object)

            # Create a new spline in the curve
            polyline = curve_data.splines.new('POLY')
            polyline.points.add(len(coords)-1)  

            # Assign the coordinates to spline points
            for i, coord in enumerate(coords):
                x, y, z = coord
                polyline.points[i].co = (x, y, z, 1)        

        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {e}")
        
        return {'FINISHED'} 

class MakeVertexToBezier(Operator):
    bl_idname = "object.vertex_to_bezier"
    bl_label = "Make a Bezier Path"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context=bpy.context):
        try:
            obj = context.active_object
            curve_resolution = context.scene.curve_resolution_u  # Get the property

            initial_mode = context.object.mode

            if initial_mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')

            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            selected_verts = [v for v in bm.verts if v.select]

            coords = [obj.matrix_world @ v.co for v in selected_verts]

            bpy.ops.object.mode_set(mode=initial_mode)

            curve_data = bpy.data.curves.new(obj.name + '_curve', type='CURVE')
            curve_data.dimensions = '3D'
            print(f"Setting resolution_u to {int(curve_resolution)}")  # Debugging Line
            
            curve_data.resolution_u = int(curve_resolution)
            
            # Check if the value is set
            print(f"Current resolution_u is {curve_data.resolution_u}")  # Debugging Line

            curve_object = bpy.data.objects.new(obj.name + '_curve', curve_data)
            curve_object.location = obj.location
            context.collection.objects.link(curve_object)

            spline = curve_data.splines.new('BEZIER')
            spline.bezier_points.add(len(coords)-1)

            for i, coord in enumerate(coords):
                x, y, z = coord
                spline.bezier_points[i].co = (x, y, z)
                spline.bezier_points[i].handle_right_type = 'AUTO'
                spline.bezier_points[i].handle_left_type = 'AUTO'

            spline.use_cyclic_u = True  # Make the curve cyclic

        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {e}")

        return {'FINISHED'}
    
class SetCameraTopView(Operator):
    bl_idname = "view3d.set_camera_top_view"
    bl_label = "Set Camera Top View"
    
    def execute(self, context):
        # Check if a camera named "Citography_top" exists
        cam = bpy.data.objects.get("Citography_top")
        
        # If it does not exist, create it
        if cam is None:
            bpy.ops.object.camera_add(location=(0, 0, 100))
            cam = bpy.context.active_object
            cam.name = "Citography_top"
        else:
            # If it exists, set it as the active object
            bpy.context.view_layer.objects.active = cam
            cam.select_set(True)
            
        # Set camera rotation for a top view
        cam.location = (0, 0, 100)  # Adjust the Z-axis as per need
        cam.rotation_euler = (0, 0, 0)  # Clear existing rotation
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 1000
            
        # Change the view to the camera view
        bpy.ops.view3d.view_camera()
        
        return {'FINISHED'}

bpy.types.Scene.path_duration = bpy.props.IntProperty(
    name="Path Duration",
    description="Set the duration that the camera will take to traverse the path",
    default=2000,
    min=1,
    max=20000
)

class SetCameraAnimationPath(Operator):
    bl_idname = "view3d.set_camera_animation_path"
    bl_label = "Set Camera Animation Path"

    path_duration: bpy.props.IntProperty(
        name="Path Duration",
        description="Set the duration that the camera will take to traverse the path",
        default=2000,  # Your default value
        min=1  # Minimum path duration
    )

    def execute(self, context):
        curve = context.active_object
        if not (curve and curve.type == 'CURVE'):
            self.report({'WARNING'}, "Active object is not a valid Bezier curve")
            return {'CANCELLED'}
        
        curve.data.path_duration = context.scene.path_duration   # Use the property value   
        
        # Create the camera and set its name
        base_name = "Citography_animation"
        suffix = 0
        while bpy.data.objects.get(f"{base_name}{suffix if suffix != 0 else ''}") is not None:
            suffix += 1
        bpy.ops.object.camera_add(location=(0, 0, 0))
        cam = context.active_object
        cam.name = f"{base_name}{suffix if suffix != 0 else ''}"
        
        # Add a Follow Path constraint to the camera
        cam_constraint = cam.constraints.new(type='FOLLOW_PATH')
        cam_constraint.target = curve
        cam_constraint.use_curve_follow = True
        
        # Create an Empty for the camera to track
        bpy.ops.object.empty_add(location=(0, 0, 0), scale=(1, 1, 1))  # Scale reduced to 1 for visibility
        empty = context.active_object
        empty.name = f"{cam.name}_Target"

        # Add Follow Path constraint to the Empty
        empty_constraint = empty.constraints.new(type='FOLLOW_PATH')
        empty_constraint.target = curve
        empty_constraint.use_curve_follow = True
        empty_constraint.offset = -9.7  # Move Empty a bit ahead

        # Make camera track the Empty
        track_constraint = cam.constraints.new(type='TRACK_TO')
        track_constraint.target = empty
        track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        track_constraint.up_axis = 'UP_Y'

        return {'FINISHED'}


class AnimateCameraAlongPath(Operator):
    bl_idname = "view3d.animate_camera_along_path"
    bl_label = "Animate Camera Along Path"
    
    def execute(self, context):
        # Ensure at least one camera exists
        if not any(obj.type == 'CAMERA' for obj in bpy.data.objects):
            self.report({'WARNING'}, "No camera exists")
            return {'CANCELLED'}
        
        # Get the last created camera or another desired one
        cam = next((obj for obj in bpy.data.objects if obj.type == 'CAMERA'), None)
        
        # Locate the Follow Path constraint and animate the path
        follow_path_constraint = next((c for c in cam.constraints if c.type == 'FOLLOW_PATH'), None)
        if follow_path_constraint is not None:
            bpy.ops.constraint.followpath_path_animate(constraint=follow_path_constraint.name, owner='OBJECT')
        else:
            self.report({'WARNING'}, "No Follow Path constraint found on the camera")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# List of classes operators
classes = [
    CleanTheScene,
    AddRandomImage,
    DistributeImagesGrid,
    SelectFolderImages,
    ImportGeoImages,
    # SimpleAddCube,
    TurnImageFlat,
    TurnImagesZRotation,
    ImportCSVFile,
    MakeVertextsToPath,
    MakeVertexToBezier,
    SetCameraTopView,
    SetCameraAnimationPath,
    AnimateCameraAlongPath,
    ImportGPXFile,
    ResetToOriginal,
    DistributeImagesSphere,
]

def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register properties
    for prop_name, prop_value in properties.items():
        setattr(bpy.types.Scene, prop_name, prop_value)


def unregister():
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister/Delete properties
    for prop_name in properties.keys():
        delattr(bpy.types.Scene, prop_name)

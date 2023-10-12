import addon_utils #to activate a check function
import os
import bpy

VALID_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')

def enable_addon(addon_name):
    # check if the addon is enabled
    loaded_default, loaded_state = addon_utils.check(addon_name)
    if not loaded_state:
        # enable the addon
        addon_utils.enable(addon_name)
    return {'FINISHED'} 

def import_images_as_plane(image_path, location=(0, 0, 0)):
    """Import an image from the path as a plane in Blender."""
    if os.path.exists(image_path):
        try:
            bpy.ops.import_image.to_plane(
                files=[{"name": os.path.basename(image_path)}],
                directory=os.path.dirname(image_path)
            )
            # Set the location of the imported image plane
            bpy.context.active_object.location = location
            return True
        except Exception as e:
            print(f"Error importing image: {e}")
            return False
    else:
        print(f"Path does not exist: {image_path}")
        return False    

def get_all_images(path):
    """Return a list of valid image files from the directory."""
    all_images = []
    for file in os.listdir(path):
        if file.lower().endswith(VALID_IMAGE_EXTENSIONS):
            all_images.append(os.path.join(path, file))
    return all_images

def format_duration(duration):
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    formatted_duration = ""
    if hours:
        formatted_duration += f"{hours}h "
    if minutes:
        formatted_duration += f"{minutes}min "
    if seconds:
        formatted_duration += f"{seconds}sec"

    return formatted_duration.strip()

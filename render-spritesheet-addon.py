bl_info = {
    "name": "Spritesheet Render",
    "author": "Mewters",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "location": "Render > Spritesheet",
    "description": "Renders the selected frames from the timeline and generates a spritesheet with ImageMagick based on the timeline markers",
    "warning": "Requires ImageMagick",
    "wiki_url": "https://github.com/mewters/blender-render-spritesheet",
    "tracker_url": "https://github.com/mewters/blender-render-spritesheet",
    "category": "Render"
}


"""
Render the selected frames from the timeline
"""

import bpy
import os
import shutil

def main(context):
    remove_frames_on_end = True
    frames_directory = "frames"
    spritesheet_directory = "spritesheets"

    scene = bpy.context.scene
    fp = scene.render.filepath # get existing output path
    scene.render.image_settings.file_format = 'PNG' # set output format to .png

    # Get a list of the markers on the timeline
    markers = scene.timeline_markers

    # set the frame range to render
    first_frame = scene.frame_start
    last_frame = scene.frame_end
    frames = range(first_frame, last_frame + 1)

    # or set the specific frames to render
    #frames = 1, 2, 3

    frame_number_length = 5 # number length to format the image file name

    generated_files = dict() # dictionary with the files names

    current_marker_name = "spritesheet";
    current_files_list = generated_files.setdefault(current_marker_name, [])

    frames_folder = os.path.join(fp, frames_directory)

    for frame_nr in frames:
        # set current frame
        scene.frame_set(frame_nr)
        
        # Get the marker at the current frame
        marker = next((m for m in markers if m.frame == frame_nr), None)

        if marker:
            current_marker_name = marker.name
            current_files_list = generated_files.setdefault(current_marker_name, [])
        
        frame_name = current_marker_name + "_" + str(frame_nr).zfill(frame_number_length)
        scene.render.filepath = os.path.join(frames_folder, frame_name)
        current_files_list.append(scene.render.filepath + ".png")
        
        bpy.ops.render.render(write_still=True) # render still

    # restore the filepath
    scene.render.filepath = fp



    """
    Get the rendered images and generate a spritesheet with ImageMagick
    """

    # Set the path of the input folder
    input_folder = fp

    spritesheet_output_dir = os.path.join(input_folder, spritesheet_directory)

    for marker, files in generated_files.items():
        
        if not os.path.isdir(spritesheet_output_dir):
            os.makedirs(spritesheet_output_dir)
        
        # Set the path of the output file
        output_file = os.path.join(spritesheet_output_dir, marker + ".png")

        # Get the list of input files in the input folder
        input_files = files

        # Calculate the size of the spritesheet image
        size = int(len(input_files) ** 0.5)

        # Use ImageMagick to create the spritesheet image
        os.system("magick montage {} -tile x{} -background none -geometry +0+0 {}".format(" ".join([os.path.join(input_folder, f) for f in input_files]), size, output_file))



    if remove_frames_on_end:
        shutil.rmtree(frames_folder)
        
        

class RenderSpritesheet(bpy.types.Operator):
    """Render the selected frames from the timeline and generates a spritesheet with ImageMagick based on the timeline markers"""
    bl_idname = "mewters.render_spritesheet"
    bl_label = "Render Spritesheet"

    def execute(self, context):
        main(context)    
        return {'FINISHED'}

class RenderSpritesheetPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Mewters"
    bl_idname = "MEWTERS_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    
    custom_text_input: bpy.props.StringProperty(name="Custom Text Input")

    def draw(self, context):
        layout = self.layout

        layout.label(text="Spritesheet:")
        row = layout.row()
        row.operator("mewters.render_spritesheet")

def register():
    bpy.utils.register_class(RenderSpritesheet)
    bpy.utils.register_class(RenderSpritesheetPanel)

def unregister():
    bpy.utils.unregister_class(RenderSpritesheet)
    bpy.utils.unregister_class(RenderSpritesheetPanel)
    
    
# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
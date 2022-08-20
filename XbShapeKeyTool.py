import struct
import bpy
import os

from bpy.props import (StringProperty,
                       PointerProperty,
                       )

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
                       
bl_info = {
    "name": "Xenoblade Shape Key Tool",
    "description": "Shape key renaming tool for Xenoblade models",
    "author": "AlexCSDev (https://github.com/AlexCSDev)",
    "blender": (2, 80, 0),
    "category": "Mesh",
}                       
                       
class XBShapeKeyToolOperator(Operator):
    bl_idname = "object.xb_shape_key_tool_operator"
    bl_label = "Xenoblade Shape Key Tool Operator"
    
    def readString(self, file):
        stringBytes = bytearray()
        byte = file.read(1)
        while byte != b'\0':
            stringBytes += byte
            byte = file.read(1)
        return stringBytes.decode("utf-8")    

    def execute(self, context):
        absolutePath = bpy.path.abspath(context.scene.xb_shapekey_tool.path)
        print(absolutePath)
        filename, file_extension = os.path.splitext(absolutePath)
        if file_extension != ".wimdo":
            self.report({"ERROR"}, "Selected file is not a WIMDO")
            return {'CANCELLED'}
        try:
            selected_object = bpy.context.object
            shape_keys = selected_object.data.shape_keys.key_blocks
        except:
            self.report({"ERROR"}, "Unable to get shape keys, make sure valid object is selected")
            return {'CANCELLED'}
        try:
            with open(absolutePath, "rb") as f:
                magic, = struct.unpack('i', f.read(4))
                if magic != 1297632580:
                    self.report({"ERROR"}, "File is not a valid WIMDO file!")
                    return {'CANCELLED'}
                f.read(4)
                modelStructOffset, = struct.unpack('i', f.read(4))
                if modelStructOffset > 0:
                    f.seek(modelStructOffset + 128)
                    morphNameTableOffset, = struct.unpack('i', f.read(4))
                    if morphNameTableOffset > 0:
                        morphTablePos = modelStructOffset + morphNameTableOffset
                        f.seek(morphTablePos)
                        f.read(4)
                        morphsCount, = struct.unpack('i', f.read(4))
						
                        if len(shape_keys) - 1 != morphsCount:
                            self.report({"ERROR"}, "Shape key count is not equal to morphs count in WIMDO. Are you loading the proper file?")
                            return {'CANCELLED'}
						
                        f.read(16)
                        for i in range(morphsCount):
                            shapeNameOffset, = struct.unpack('i', f.read(4))
                            morphNameOffset, = struct.unpack('i', f.read(4))
                            f.read(20)
                            print(f'Morph {i}: {shapeNameOffset}, {morphNameOffset}')
                            currentPos = f.tell()
                            f.seek(morphTablePos + shapeNameOffset)
                            shapeMeshName = self.readString(f)
                            print(f'Shape mesh name: {shapeMeshName}')
                            f.seek(morphTablePos + morphNameOffset)
                            morphName = self.readString(f)
                            print(f'Morph name: {morphName}')
                            f.seek(currentPos)
                            shape_keys[i + 1].name = morphName
                    else:
                        self.report({"ERROR"}, "Unable to find morph name table offset in the file! Is the file corrupted?")
                        return {'CANCELLED'}    
                else:
                    self.report({"ERROR"}, "Unable to find model struct offset in the file! Is the file corrupted?")
                    return {'CANCELLED'}                   				
            self.report({"INFO"}, "Shape keys successfully renamed")
            return {'FINISHED'}
                            
        except Exception as e: 
            print(e)
            self.report({"ERROR"}, "Error while reading the file! Error has been printed to system console.")
            return {'CANCELLED'}

class XBShapeKeyToolProperties(PropertyGroup):

    path : StringProperty(
        name="",
        description="Path to wimdo",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

class OBJECT_PT_XBShapeKeyToolPanel(Panel):
    bl_idname = "OBJECT_PT_XBShapeKeyToolPanel"
    bl_label = "Xenoblade Shape Key Tool"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Xenoblade"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        col.prop(scn.xb_shapekey_tool, "path", text="")
        layout.separator()
        col = layout.column(align=True)
        col.operator(XBShapeKeyToolOperator.bl_idname, text="Fill shape keys", icon="MODIFIER")

classes = (
    XBShapeKeyToolProperties,
    OBJECT_PT_XBShapeKeyToolPanel,
    XBShapeKeyToolOperator
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.xb_shapekey_tool = PointerProperty(type=XBShapeKeyToolProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.xb_shapekey_tool


if __name__ == "__main__":
    register()
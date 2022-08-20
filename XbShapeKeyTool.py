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
        print (context.scene.xb_shapekey_tool.path)
        filename, file_extension = os.path.splitext(context.scene.xb_shapekey_tool.path)
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
            with open(context.scene.xb_shapekey_tool.path, "rb") as f:
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
            self.report({"INFO"}, "Shape keys successfully renamed")
            return {'FINISHED'}
                            
        except:
            self.report({"ERROR"}, "Error while reading the file!")
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
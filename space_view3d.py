import bpy
import mathutils
import bgl
import math
import os
from . import unit
from bpy_extras.view3d_utils import location_3d_to_region_2d

ISRING = "ISRING"
ISWALL = "ISWALL"
ISROOMMESH = "ISROOMMESH"
RING_DIAMETER_PATH = os.path.join(os.path.dirname(__file__),"Assets","Ring_Sizes.blend")
RING_PROFILE_PATH = os.path.join(os.path.dirname(__file__),"Assets","Ring_Profiles.blend")
PATTERN_CATEGORIES = os.path.join(os.path.dirname(__file__),"Assets","Patterns")

def create_image_preview_collection():
    import bpy.utils.previews
    col = bpy.utils.previews.new()
    col.my_previews_dir = ""
    col.my_previews = ()
    return col

preview_collections = {}   
preview_collections["ring_diameter"] = create_image_preview_collection()
preview_collections["ring_profile"] = create_image_preview_collection()
preview_collections["pattern_categories"] = create_image_preview_collection()
preview_collections["pattern_items"] = create_image_preview_collection()

def get_obj_names_enum_previews(path,key,force_reload=False,include_none=False):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the images from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews

    if include_none:
        enum_items.append(("None", "None", "None"))  

    with bpy.data.libraries.load(path, False, False) as (data_from, data_to):
        for i, obj in enumerate(data_from.objects):
            enum_items.append((obj, obj, obj))            

    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def get_folder_enum_previews(path,key):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the folders from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        folders = []
        for fn in os.listdir(path):
            if os.path.isdir(os.path.join(path,fn)):
                folders.append(fn)

        for i, name in enumerate(folders):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, "", 'IMAGE')
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def get_image_enum_previews(path,key,force_reload=False):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the images from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        image_paths = []
        for fn in os.listdir(path):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, filepath, 'IMAGE',force_reload)
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def enum_pattern_categories(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(PATTERN_CATEGORIES)
    pcoll = preview_collections["pattern_categories"]
    return get_folder_enum_previews(icon_dir,pcoll)

def enum_pattern_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(PATTERN_CATEGORIES,self.pattern_category)
    pcoll = preview_collections["pattern_items"]
    return get_image_enum_previews(icon_dir,pcoll)

def update_pattern_category(self,context):
    if preview_collections["pattern_items"]:
        bpy.utils.previews.remove(preview_collections["pattern_items"])
        preview_collections["pattern_items"] = create_image_preview_collection()     
        
    enum_pattern_names(self,context)

def update_ring_diameter(self,context):
    print("TODO: UPATE RING DIAMETER")

def enum_ring_profile(self,context):
    if context is None:
        return []
    
    icon_dir = RING_PROFILE_PATH
    pcoll = preview_collections["ring_profile"]
    return get_obj_names_enum_previews(icon_dir,pcoll,include_none=True)

def get_ring_profile(self,context):
    pass

def update_ring_profile(self,context):
    ring_obj = context.object
    obj_print_props = ring_obj.printing3d
    scene = context.scene
    profile_obj = None
    
    if obj_print_props.ring_profile in bpy.data.objects:
        profile_obj = bpy.data.objects[obj_print_props.ring_profile]
    
    if not profile_obj:
        with bpy.data.libraries.load(RING_PROFILE_PATH, False, False) as (data_from, data_to):
            for i, obj in enumerate(data_from.objects):
                if obj == obj_print_props.ring_profile:
                    data_to.objects = [obj]
                    
        for obj in data_to.objects:
            profile_obj = obj
    
    ring_obj.data.bevel_object = profile_obj
    

def clear_view3d_properties_shelf():
    if hasattr(bpy.types, 'VIEW3D_PT_grease_pencil'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_grease_pencil)
    if hasattr(bpy.types, 'VIEW3D_PT_grease_pencil_palettecolor'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_grease_pencil_palettecolor)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_properties'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_properties)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_cursor'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_cursor)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_name'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_name)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_display'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_display)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_stereo'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_stereo)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_shading'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_shading)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_motion_tracking'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_motion_tracking)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_meshdisplay'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_meshdisplay)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_meshstatvis'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_meshstatvis)
    if hasattr(bpy.types, 'VIEW3D_PT_view3d_curvedisplay'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_view3d_curvedisplay)
    if hasattr(bpy.types, 'VIEW3D_PT_background_image'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_background_image)
    if hasattr(bpy.types, 'VIEW3D_PT_transform_orientations'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_transform_orientations)
    if hasattr(bpy.types, 'VIEW3D_PT_etch_a_ton'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_etch_a_ton)
    if hasattr(bpy.types, 'VIEW3D_PT_context_properties'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_context_properties)
    if hasattr(bpy.types, 'VIEW3D_PT_tools_animation'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_animation)
    if hasattr(bpy.types, 'VIEW3D_PT_tools_relations'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_relations)        
    if hasattr(bpy.types, 'VIEW3D_PT_tools_rigid_body'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_rigid_body)   

def clear_view3d_tools_shelf():
    if hasattr(bpy.types, 'VIEW3D_PT_tools_grease_pencil_brush'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_grease_pencil_brush)     
    if hasattr(bpy.types, 'VIEW3D_PT_tools_grease_pencil_draw'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_grease_pencil_draw)     
    if hasattr(bpy.types, 'VIEW3D_PT_tools_add_object'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_add_object)  
    if hasattr(bpy.types, 'VIEW3D_PT_tools_transform'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_transform)            
    if hasattr(bpy.types, 'VIEW3D_PT_tools_object'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_object)            
    if hasattr(bpy.types, 'VIEW3D_PT_tools_history'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_PT_tools_history)

def clear_view3d_header():
    if hasattr(bpy.types, 'VIEW3D_HT_header'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_HT_header)   

def clear_view3d_menus():
    if hasattr(bpy.types, 'VIEW3D_MT_view'):
        bpy.utils.unregister_class(bpy.types.VIEW3D_MT_view)

def scene_rings(scene):
    for obj in scene.objects:
        if ISRING in obj:
            yield obj

class VIEW3D_HT_header(bpy.types.Header):
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        layout = self.layout

        obj = context.active_object

        row = layout.row(align=True)
        
        row.template_header()
        
        VIEW3D_MT_menus.draw_collapsible(context, layout)
        
        if context.space_data.viewport_shade == 'WIREFRAME':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Wire Frame",icon='WIRE')
        if context.space_data.viewport_shade == 'SOLID':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Solid",icon='SOLID')
        if context.space_data.viewport_shade == 'MATERIAL':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Material",icon='MATERIAL')
        if context.space_data.viewport_shade == 'RENDERED':
            layout.operator_menu_enum("view3d.change_shademode","shade_mode",text="Rendered",icon='SMOOTH')

        row = layout.row()
        row.prop(context.space_data,"pivot_point",text="")
        
        row = layout.row(align=True)
        row.prop(context.space_data,"show_manipulator",text="")
        row.prop(context.space_data,"transform_manipulators",text="")
        row.prop(context.space_data,"transform_orientation",text="")
        
#         if obj:
#             if obj.type in {'MESH','CURVE'}:
#                 if obj.mode == 'EDIT':
#                     layout.operator_menu_enum('fd_general.change_mode',"mode",icon='EDITMODE_HLT',text="Edit Mode")
#                 else:
#                     layout.operator_menu_enum('fd_general.change_mode',"mode",icon='OBJECT_DATAMODE',text="Object Mode")
                
        row = layout.row(align=True)
        row.operator('view3d.ruler',text="Ruler")

class VIEW3D_MT_menus(bpy.types.Menu):
    bl_space_type = 'VIEW3D_MT_editor_menus'
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        layout.menu("VIEW3D_MT_view",icon='VIEWZOOM',text="   View   ")
        layout.menu("VIEW3D_MT_add_object",icon='GREASEPENCIL',text="   Add   ")
        layout.menu("VIEW3D_MT_tools",icon='MODIFIER',text="   Tools   ")

class VIEW3D_MT_view(bpy.types.Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        layout.operator("view3d.toolshelf",icon='MENU_PANEL')
        layout.operator("view3d.properties",icon='MENU_PANEL')
        layout.separator()
        layout.operator("view3d.view_all",icon='VIEWZOOM')
        layout.operator("view3d.view_selected",text="Zoom To Selected",icon='ZOOM_SELECTED')

        layout.separator()

        layout.operator("view3d.navigate",icon='RESTRICT_VIEW_OFF',text="First Person View")
        
        layout.separator()

        layout.operator("view3d.viewnumpad", text="Camera",icon='CAMERA_DATA').type = 'CAMERA'
        layout.operator("view3d.viewnumpad", text="Top",icon='TRIA_DOWN').type = 'TOP'
        layout.operator("view3d.viewnumpad", text="Front",icon='TRIA_UP').type = 'FRONT'
        layout.operator("view3d.viewnumpad", text="Left",icon='TRIA_LEFT').type = 'LEFT'
        layout.operator("view3d.viewnumpad", text="Right",icon='TRIA_RIGHT').type = 'RIGHT'

        layout.separator()

        layout.operator("view3d.view_persportho",icon='SCENE')
        
        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.separator()

        layout.operator("screen.area_dupli",icon='GHOST')
        layout.operator("screen.region_quadview",icon='IMGDISPLAY')
        layout.operator("screen.screen_full_area",icon='FULLSCREEN_ENTER')    
        
        layout.separator()
        
        layout.operator("space_view3d.viewport_options",text="Viewport Settings...",icon='SCRIPTPLUGINS')

class VIEW3D_MT_add_object(bpy.types.Menu):
    bl_label = "Add Object"

    def draw(self, context):
        layout = self.layout

        # note, don't use 'EXEC_SCREEN' or operators wont get the 'v3d' context.

        # Note: was EXEC_AREA, but this context does not have the 'rv3d', which prevents
        #       "align_view" to work on first call (see [#32719]).
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("view3d.draw_mesh", icon='MESH_GRID')

        layout.operator_context = 'EXEC_REGION_WIN'
        layout.separator()
        layout.menu("INFO_MT_mesh_add", icon='OUTLINER_OB_MESH')

        layout.menu("INFO_MT_curve_add", icon='OUTLINER_OB_CURVE')
        layout.operator_context = 'EXEC_REGION_WIN'
        layout.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')
        layout.separator()

        layout.operator_menu_enum("object.empty_add", "type", text="Empty", icon='OUTLINER_OB_EMPTY')
        layout.separator()
        layout.operator("view3d.add_camera",text="Camera",icon='OUTLINER_OB_CAMERA')
        layout.menu("VIEW3D_MT_add_lamp", icon='OUTLINER_OB_LAMP')
        layout.separator()
        
        if len(bpy.data.groups) > 10:
            layout.operator_context = 'INVOKE_REGION_WIN'
            layout.operator("object.group_instance_add", text="Group Instance...", icon='OUTLINER_OB_EMPTY')
        else:
            layout.operator_menu_enum("object.group_instance_add", "group", text="Group Instance", icon='OUTLINER_OB_EMPTY')

class VIEW3D_MT_add_lamp(bpy.types.Menu):
    bl_label = "Lamp"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.lamp_add",icon='LAMP_POINT',text="Add Point Lamp").type = 'POINT'
        layout.operator("object.lamp_add",icon='LAMP_SUN',text="Add Sun Lamp").type = 'SUN'
        layout.operator("object.lamp_add",icon='LAMP_SPOT',text="Add Spot Lamp").type = 'SPOT'
        layout.operator("object.lamp_add",icon='LAMP_AREA',text="Add Area Lamp").type = 'AREA'

class VIEW3D_MT_tools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Object"

    def draw(self, context):
        layout = self.layout
        layout.menu("VIEW3D_MT_objecttools",icon='OBJECT_DATA')
        layout.menu("VIEW3D_MT_cursor_tools",icon='CURSOR')
        layout.menu("VIEW3D_MT_selectiontools",icon='MAN_TRANS')
        layout.separator()
        layout.operator("view3d.snapping_options",icon='SNAP_ON')

class VIEW3D_MT_cursor_tools(bpy.types.Menu):
    bl_label = "Cursor Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator('view3d.set_cursor_location',text="Set Cursor Location...",icon='CURSOR')
        layout.separator()
        layout.operator("view3d.snap_cursor_to_selected",icon='CURSOR')
        layout.operator("view3d.snap_cursor_to_center",icon='GRID')
        layout.operator("view3d.snap_selected_to_cursor",icon='SPACE2')

class VIEW3D_MT_transformtools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Transforms"

    def draw(self, context):
        layout = self.layout
        layout.operator("transform.translate",text='Grab',icon='MAN_TRANS')
        layout.operator("transform.rotate",icon='MAN_ROT')
        layout.operator("transform.resize",text="Scale",icon='MAN_SCALE')

class VIEW3D_MT_selectiontools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Selection Tools"

    def draw(self, context):
        layout = self.layout
        if context.active_object:
            if context.active_object.mode == 'OBJECT':
                layout.operator("object.select_all",text='Toggle De/Select',icon='MAN_TRANS')
            else:
                layout.operator("mesh.select_all",text='Toggle De/Select',icon='MAN_TRANS')
        else:
            layout.operator("object.select_all",text='Toggle De/Select',icon='MAN_TRANS')
        layout.operator("view3d.select_border",icon='BORDER_RECT')
        layout.operator("view3d.select_circle",icon='BORDER_LASSO')
        if context.active_object and context.active_object.mode == 'EDIT':    
            layout.separator()
            layout.menu('VIEW3D_MT_mesh_selection',text="Mesh Selection",icon='MAN_TRANS')

class VIEW3D_MT_origintools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Origin Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.origin_set",text="Origin to Cursor",icon='CURSOR').type = 'ORIGIN_CURSOR'
        layout.operator("object.origin_set",text="Origin to Geometry",icon='CLIPUV_HLT').type = 'ORIGIN_GEOMETRY'
        
class VIEW3D_MT_shadetools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Object Shading"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.shade_smooth",icon='SOLID')
        layout.operator("object.shade_flat",icon='SNAP_FACE')

class VIEW3D_MT_objecttools(bpy.types.Menu):
    bl_context = "objectmode"
    bl_label = "Object Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("transform.translate",text='Grab',icon='MAN_TRANS')
        layout.operator("transform.rotate",icon='MAN_ROT')
        layout.operator("transform.resize",text="Scale",icon='MAN_SCALE')        
#         layout.menu("VIEW3D_MT_transformtools",icon='MAN_TRANS')
        layout.separator()
        layout.operator("object.duplicate_move",icon='PASTEDOWN')
        layout.operator("object.convert", text="Convert to Mesh",icon='MOD_REMESH').target = 'MESH'
        layout.operator("object.join",icon='ROTATECENTER')
        layout.separator()
        layout.menu("VIEW3D_MT_selectiontools",icon='MOD_MULTIRES')            
        layout.separator()
        layout.menu("VIEW3D_MT_origintools",icon='SPACE2')
        layout.separator()
        layout.menu("VIEW3D_MT_shadetools",icon='MOD_MULTIRES')
        layout.separator()
        layout.operator("object.delete",icon='X').use_global = False

class VIEW3D_MT_mesh_selection(bpy.types.Menu):
    bl_label = "Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.select_mode",text="Vertex Select",icon='VERTEXSEL').type='VERT'
        layout.operator("mesh.select_mode",text="Edge Select",icon='EDGESEL').type='EDGE'
        layout.operator("mesh.select_mode",text="Face Select",icon='FACESEL').type='FACE'

class OPS_viewport_options(bpy.types.Operator):
    bl_idname = "space_view3d.viewport_options"
    bl_label = "Viewport Options"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        view = context.space_data

        camera_box = layout.box()
        camera_box.label("Viewport Options",icon='SCENE')
        camera_box.prop(context.space_data,"lens",text="Viewport Lens Angle")
        row = camera_box.row()
        row.prop(context.space_data,"clip_start",text="Viewport Clipping Start")
        row.prop(context.space_data,"clip_end",text="Viewport Clipping End")
        layout.separator()
        camera_box.prop(context.space_data,"lock_camera",text="Lock Camera to View")

        col = camera_box.column()
        col.prop(view, "show_only_render")
        col.prop(view, "show_world")

        col = camera_box.column()
        col.prop(view, "show_outline_selected")
        col.prop(view, "show_all_objects_origin")
        col.prop(view, "show_relationship_lines")

        grid_box = layout.box()
        grid_box.label("Grid Options",icon='GRID')
        
        col = grid_box.column()
        split = col.split(percentage=0.55)
        split.prop(view, "show_floor", text="Grid Floor")

        row = split.row(align=True)
        row.prop(view, "show_axis_x", text="X", toggle=True)
        row.prop(view, "show_axis_y", text="Y", toggle=True)
        row.prop(view, "show_axis_z", text="Z", toggle=True)

        sub = col.column(align=True)
        sub.active = bool(view.show_floor or view.region_quadviews or not view.region_3d.is_perspective)
        subsub = sub.column(align=True)
        subsub.active = view.show_floor
        subsub.prop(view, "grid_lines", text="Lines")
        sub.prop(view, "grid_scale", text="Scale")

class OPS_change_shademode(bpy.types.Operator):
    bl_idname = "view3d.change_shademode"
    bl_label = "Change Shademode"

    shade_mode = bpy.props.EnumProperty(
            name="Shade Mode",
            items=(('WIREFRAME', "Wire Frame", "WIREFRAME",'WIRE',1),
                   ('SOLID', "Solid", "SOLID",'SOLID',2),
                   ('MATERIAL', "Material","MATERIAL",'MATERIAL',3),
                   ('RENDERED', "Rendered", "RENDERED",'SMOOTH',4)
                   ),
            )

    def execute(self, context):
        context.scene.render.engine = 'CYCLES'
        context.space_data.viewport_shade = self.shade_mode
        return {'FINISHED'}



class OPS_add_camera(bpy.types.Operator):
    bl_idname = "view3d.add_camera"
    bl_label = "Add Camera"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.camera_add(view_align=False)
        camera = context.active_object
        bpy.ops.view3d.camera_to_view()
        camera.data.clip_start = unit.inch(1)
        camera.data.clip_end = 9999
        camera.data.ortho_scale = 200.0
        return {'FINISHED'}

class OPS_set_cursor_location(bpy.types.Operator):
    bl_idname = "view3d.set_cursor_location"
    bl_label = "Cursor Location"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene,"cursor_location",text="")

class OPS_snapping_options(bpy.types.Operator):
    bl_idname = "view3d.snapping_options"
    bl_label = "Snapping Options"

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        toolsettings = context.tool_settings
        obj = context.object
        if not obj or obj.mode not in {'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'}:
            snap_element = toolsettings.snap_element
#             row = layout.row(align=True)
            if toolsettings.use_snap:
                layout.prop(toolsettings, "use_snap", text="Snapping On")
                layout.label("Tip: Hold Ctrl to deactivate snapping when snapping is turned ON")
            else:
                layout.prop(toolsettings, "use_snap", text="Snapping Off")
                layout.label("Tip: Hold Ctrl to activate snapping when snapping is turned OFF")
                
            layout.prop(toolsettings, "snap_element", icon_only=False)
            if snap_element == 'INCREMENT':
                layout.prop(toolsettings, "use_snap_grid_absolute")
            else:
                layout.prop(toolsettings, "snap_target")
                if obj:
                    if obj.mode in {'OBJECT', 'POSE'} and snap_element != 'VOLUME':
                        layout.prop(toolsettings, "use_snap_align_rotation")
                    elif obj.mode == 'EDIT':
                        layout.prop(toolsettings, "use_snap_self")

            if snap_element == 'VOLUME':
                layout.prop(toolsettings, "use_snap_peel_object")
            elif snap_element == 'FACE':
                layout.prop(toolsettings, "use_snap_project")

def enum_ring_diameter(self,context):
    if context is None:
        return []
    
    icon_dir = RING_DIAMETER_PATH
    pcoll = preview_collections["ring_diameter"]
    return get_obj_names_enum_previews(icon_dir,pcoll)

class OPS_fix_curve_scale(bpy.types.Operator):
    bl_idname = "view3d.fix_curve_scale"
    bl_label = "Fix Curve Scale"
    
    obj_name = bpy.props.StringProperty(name='Obj Name')
    
    def execute(self, context):
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = context.scene.objects[self.obj_name]  
        obj.hide_select = False
        obj.select = True
        context.scene.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True) 
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.radius_set()
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


class OPS_add_ring(bpy.types.Operator):
    bl_idname = "view3d.add_ring"
    bl_label = "Add Ring"

    ring_diameter = bpy.props.EnumProperty(name="Ring Diameter",items=enum_ring_diameter)
    ring_profile = bpy.props.EnumProperty(name="Ring Profile",items=enum_ring_profile)
    
    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return True

    def get_ring_diameter_object(self,context):
        scene = context.scene
        print_props = scene.printing3d      
        with bpy.data.libraries.load(RING_DIAMETER_PATH, False, False) as (data_from, data_to):
            for i, obj in enumerate(data_from.objects):
                if obj == self.ring_diameter:
                    data_to.objects = [obj]
        for obj in data_to.objects:
            scene.objects.link(obj)
            return obj

    def execute(self, context):
        scene = context.scene
        print_props = scene.printing3d   
        obj = self.get_ring_diameter_object(context)   
        obj.hide = False
        obj.hide_select = False
        obj.select = True
        obj[ISRING] = True
        scene.objects.active = obj
        bpy.ops.view3d.view_selected()
        obj_print_props = obj.printing3d
        obj_print_props.ring_profile = self.ring_profile
#         with bpy.data.libraries.load(RING_DIAMETER_PATH, False, False) as (data_from, data_to):
#             for i, obj in enumerate(data_from.objects):
#                 if obj == print_props.ring_diameter:
#                     data_to.objects = [obj]
#         for obj in data_to.objects:
#             scene.objects.link(obj)
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self,'ring_diameter')
        layout.prop(self,'ring_profile')
        
class OPS_delete_ring(bpy.types.Operator):
    bl_idname = "view3d.delete_ring"
    bl_label = "Delete Ring"
    
    ring_name = bpy.props.StringProperty(name="Ring Name")

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        print_props = scene.printing3d   
        obj = context.scene.objects[self.ring_name]  
        obj.hide = False
        obj.hide_select = False
        obj.select = True
        scene.objects.active = obj
        
        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the ring?")      
        
class OPS_add_pattern(bpy.types.Operator):
    bl_idname = "view3d.add_pattern"
    bl_label = "Select Pattern"
    
    obj_name = bpy.props.StringProperty(name="Obj Name")
    pattern_category = bpy.props.EnumProperty(name="Pattern Category",items=enum_pattern_categories,update=update_pattern_category)
    pattern_name = bpy.props.EnumProperty(name="Pattern Name",items=enum_pattern_names)
    auto_wrap_pattern = bpy.props.BoolProperty(name="Auto Wrap Pattern")
    
    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return True

    def get_pattern_object(self,context):
        path = "" #path to Blend File
        #GET OBJECT
        scene = context.scene
        print_props = scene.printing3d
        patten_path = os.path.join(PATTERN_CATEGORIES ,self.pattern_category,self.pattern_name + ".blend")
        with bpy.data.libraries.load(patten_path, False, False) as (data_from, data_to):
            for i, obj in enumerate(data_from.objects):
                data_to.objects = [obj]
                break
        for obj in data_to.objects:
            scene.objects.link(obj)
            return obj

    def execute(self, context):
        scene = context.scene
        parent = scene.objects[self.obj_name]
        print_props = scene.printing3d   
        obj = self.get_pattern_object(context)   
        obj.parent = parent
        obj.hide = False
        obj.hide_select = False
        obj.select = True
        if self.auto_wrap_pattern:
            array_mod = obj.modifiers.new("Length Array",'ARRAY')
            array_mod.relative_offset_displace = (0,1,0)

            curve_mod = obj.modifiers.new("Follow Curve",'CURVE')
            curve_mod.object = parent
            curve_mod.deform_axis = 'POS_Y'
        
        scene.objects.active = obj
        bpy.ops.view3d.view_selected()
        #IF AUTOWRAP THEN ADD NEEDED MODIFIERS

        return {'FINISHED'}
        
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self,'pattern_category',text="",icon='FILE_FOLDER')  
        layout.template_icon_view(self,"pattern_name",show_labels=True)  
        layout.label(self.pattern_name)
        layout.prop(self,'auto_wrap_pattern')

class VIEW3D_PT_printing3d(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "3D Prining"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        print_props = scene.printing3d
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(print_props, "main_object_selection", 'Rings', icon='CURVE_BEZCIRCLE', text="Rings") 
        row.prop_enum(print_props, "main_object_selection", 'Bracelets', icon='CURVE_NCURVE', text="Bracelets") 
        row.prop_enum(print_props, "main_object_selection", 'Earrings', icon='CURVE_BEZCURVE', text="Earrings") 
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(print_props, "main_object_selection", 'Pendent', icon='MOD_SKIN', text="Pendent") 
        row.prop_enum(print_props, "main_object_selection", 'Necklace', icon='CURVE_NCIRCLE', text="Necklace")      
        row.prop_enum(print_props, "main_object_selection", 'Sculptures', icon='MOD_ARMATURE', text="Sculptures")
        
        box = col.box()
        if print_props.main_object_selection == 'Rings':
            row = box.row()
            row.scale_y = 1.2
            row.operator("view3d.add_ring",text="Add Ring",icon='ZOOMIN')

            for obj in scene_rings(scene):

                col.separator()
                ring_box = col.box() 
                row = ring_box.row()   
                row.label("Ring: " + obj.name,icon='CURVE_BEZCIRCLE')  
                row.prop(obj,'hide',text="",emboss=False)
                row.operator('view3d.fix_curve_scale',text="",icon='MAN_SCALE',emboss=False).obj_name = obj.name
                row.operator('view3d.delete_ring',text="",icon='X',emboss=False)         
                row = ring_box.row()
                row.label("Ring Name:")
                row.prop(obj,'name',text="")
                row = ring_box.row()
                row.label("Ring Profile:")
                row.prop(context.object.printing3d,'ring_profile',text="")
                
                pattern_box = col.box()
                pattern_row = pattern_box.row()
                pattern_row.operator("view3d.add_pattern",text="Add Pattern",icon='ZOOMIN').obj_name = obj.name
            
                for child in obj.children:
                    pattern_box.label(child.name)
                    pattern_box.prop(child.data,'bevel_object')
            
        if print_props.main_object_selection == 'Bracelets':
            row = box.row()
            row.label("UNDER DEVELOPMENT!")
            # Change Diameter
            # Change Ring Profile
            # Add Pattern            
            
        if print_props.main_object_selection == 'Earrings':
            row = box.row()
            row.label("UNDER DEVELOPMENT!")
            # Change Diameter
            # Change Ring Profile
            # Add Pattern                      
            
        if print_props.main_object_selection == 'Pendent':
            row = box.row()
            row.label("UNDER DEVELOPMENT!")
            # Change Diameter
            # Change Ring Profile
            # Add Pattern                     
            
        if print_props.main_object_selection == 'Necklace':
            row = box.row()
            row.label("UNDER DEVELOPMENT!")
            # Change Diameter
            # Change Ring Profile
            # Add Pattern                     
            
        if print_props.main_object_selection == 'Sculptures':
            row = box.row()
            row.label("UNDER DEVELOPMENT!")
            # Change Diameter
            # Change Ring Profile
            # Add Pattern                            
            
        # Prepare for Printing
        # Export File
        # Upload to Shapeways    

class PROPS_Scene_printing3d(bpy.types.PropertyGroup):
    
    main_object_selection = bpy.props.EnumProperty(name="Main Object Selection",
                                                   items=[('Rings','Rings','Rings'),
                                                          ('Bracelets','Bracelets','Bracelets'),
                                                          ('Earrings','Earrings','Earrings'),
                                                          ('Pendent','Pendent','Pendent'),
                                                          ('Necklace','Necklace','Necklace'),
                                                          ('Sculptures','Sculptures','Sculptures')])
    

    ring_profile = bpy.props.EnumProperty(name="Ring Profile",items=enum_ring_profile)
    
#     def get_ring_diameter_object(self,context):
#         
#         scene = context.scene
#         print_props = scene.printing3d      
#         with bpy.data.libraries.load(RING_DIAMETER_PATH, False, False) as (data_from, data_to):
#             for i, obj in enumerate(data_from.objects):
#                 if obj == print_props.ring_diameter:
#                     data_to.objects = [obj]
#         for obj in data_to.objects:
#             scene.objects.link(obj)
#             return obj
    
class PROPS_Object_printing3d(bpy.types.PropertyGroup):
    
    ring_profile = bpy.props.EnumProperty(name="Ring Profile",items=enum_ring_profile,update=update_ring_profile)
    
def register():
    clear_view3d_properties_shelf()
    clear_view3d_tools_shelf()
    clear_view3d_header()
    clear_view3d_menus()
    
    bpy.utils.register_class(PROPS_Scene_printing3d)
    bpy.types.Scene.printing3d = bpy.props.PointerProperty(type = PROPS_Scene_printing3d)
    
    bpy.utils.register_class(PROPS_Object_printing3d)
    bpy.types.Object.printing3d = bpy.props.PointerProperty(type = PROPS_Object_printing3d)    
    
    bpy.utils.register_class(VIEW3D_HT_header)
    bpy.utils.register_class(VIEW3D_MT_menus)
    bpy.utils.register_class(VIEW3D_MT_view)
    bpy.utils.register_class(VIEW3D_MT_add_object)
    bpy.utils.register_class(VIEW3D_MT_add_lamp)
    bpy.utils.register_class(VIEW3D_MT_tools)
    bpy.utils.register_class(VIEW3D_MT_cursor_tools) 
    bpy.utils.register_class(VIEW3D_MT_transformtools) 
    bpy.utils.register_class(VIEW3D_MT_selectiontools) 
    bpy.utils.register_class(VIEW3D_MT_origintools) 
    bpy.utils.register_class(VIEW3D_MT_shadetools) 
    bpy.utils.register_class(VIEW3D_MT_objecttools) 
    bpy.utils.register_class(VIEW3D_MT_mesh_selection)  
    bpy.utils.register_class(OPS_viewport_options)
    bpy.utils.register_class(OPS_change_shademode)
    bpy.utils.register_class(OPS_add_camera)
    bpy.utils.register_class(OPS_set_cursor_location)
    bpy.utils.register_class(OPS_snapping_options)    
    bpy.utils.register_class(OPS_fix_curve_scale)
    bpy.utils.register_class(OPS_add_ring)
    bpy.utils.register_class(OPS_delete_ring)
    bpy.utils.register_class(OPS_add_pattern)
    bpy.utils.register_class(VIEW3D_PT_printing3d)    
    
    
def unregister():
    pass
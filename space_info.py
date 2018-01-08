import bpy

class INFO_HT_header(bpy.types.Header):
    bl_space_type = 'INFO'

    def draw(self, context):
        layout = self.layout

        window = context.window
        scene = context.scene
        rd = scene.render

        row = layout.row(align=True)
        row.template_header()
        INFO_MT_menus.draw_collapsible(context, layout)
        if window.screen.show_fullscreen:
            layout.operator("screen.back_to_previous", icon='SCREEN_BACK', text="Back to Previous")
            layout.separator()
        else:
            pass
#             layout.template_ID(context.window, "screen", new="screen.new", unlink="screen.delete")
        layout.separator()
        if context.active_object:
            if context.active_object.mode == 'EDIT':
                layout.label('You are currently in Edit Mode type the TAB key to return to object mode',icon='ERROR')

        layout.template_running_jobs()

        layout.template_reports_banner()

        row = layout.row(align=True)

        if bpy.app.autoexec_fail is True and bpy.app.autoexec_fail_quiet is False:
            layout.operator_context = 'EXEC_DEFAULT'
            row.label("Auto-run disabled: %s" % bpy.app.autoexec_fail_message, icon='ERROR')
            if bpy.data.is_saved:
                props = row.operator("wm.open_mainfile", icon='SCREEN_BACK', text="Reload Trusted")
                props.filepath = bpy.data.filepath
                props.use_scripts = True

            row.operator("script.autoexec_warn_clear", text="Ignore")
            return
        
#         if rd.has_multiple_engines:
#             row.prop(rd, "engine", text="")        
        
        row.label(text=scene.statistics(), translate=False)
            
            
class INFO_MT_menus(bpy.types.Menu):
    bl_idname = "INFO_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        layout.menu("INFO_MT_file",icon='FILE_FOLDER',text="   File   ")
        layout.menu("INFO_MT_edit",icon='RECOVER_AUTO',text="   Edit   ")
        layout.menu("INFO_MT_rendering",icon='RENDER_STILL',text="   Export    ")
        layout.menu("INFO_MT_rendering",icon='RENDER_STILL',text="   Render    ")
        layout.menu("INFO_MT_help",icon='HELP',text="   Help   ")

class INFO_MT_file(bpy.types.Menu):
    bl_label = "File"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.read_homefile", text="New", icon='NEW')
        layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER')
        layout.menu("INFO_MT_file_open_recent", icon='OPEN_RECENT')
        layout.operator("wm.recover_last_session", icon='RECOVER_LAST')
        layout.operator("wm.recover_auto_save", text="Recover Auto Save...", icon='RECOVER_AUTO')

        layout.separator()

        layout.operator_context = 'EXEC_AREA' if context.blend_data.is_saved else 'INVOKE_AREA'
        layout.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.save_as_mainfile", text="Save As...", icon='SAVE_AS')
        
        layout.separator()

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.link", text="Link", icon='LINK_BLEND')
        layout.operator("wm.append", text="Append", icon='APPEND_BLEND')

        layout.separator()

        layout.operator("screen.userpref_show", text="User Preferences...", icon='PREFERENCES')
        layout.separator()
        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.save_homefile", icon='SAVE_PREFS')
        layout.operator("wm.read_factory_settings", icon='LOAD_FACTORY')

        layout.separator()

        layout.menu("INFO_MT_file_import", icon='IMPORT')
        layout.menu("INFO_MT_file_export", icon='EXPORT')
        
        layout.separator()
    
        if any(bpy.utils.app_template_paths()):
            app_template = context.user_preferences.app_template
            if app_template:
                layout.operator(
                    "wm.read_factory_settings",
                    text="Load Factory Template Settings",
                    icon='LOAD_FACTORY',
                ).app_template = app_template
            del app_template
        
        layout.menu("USERPREF_MT_app_templates", icon='FILE_BLEND')        
        
        layout.separator()
        
        layout.menu("INFO_MT_addons", icon='PLUGIN')
        
        layout.separator()

        layout.menu("INFO_MT_file_external_data", icon='EXTERNAL_DATA')

        layout.separator()

        layout.operator_context = 'EXEC_AREA'
        layout.operator("wm.quit_blender", text="Quit", icon='QUIT')
        
class INFO_MT_edit(bpy.types.Menu):
    bl_idname = "INFO_MT_edit"
    bl_label = "Edit"

    def draw(self, context):
        layout = self.layout
        layout.operator("ed.undo",icon='LOOP_BACK')
        layout.operator("ed.redo",icon='LOOP_FORWARDS')
        layout.operator("ed.undo_history",icon='RECOVER_LAST')        
        
class INFO_MT_rendering(bpy.types.Menu):
    bl_label = "Rendering"

    def draw(self, context):
        layout = self.layout
        layout.operator("render.render", text="Render Image", icon='RENDER_STILL').use_viewport = True
        layout.operator("render.opengl", text="Render OpenGL")
        layout.separator()
        layout.operator("info.render_settings",text="Render Settings",icon='INFO')        
        
class OPS_render_settings(bpy.types.Operator): 
    bl_idname = "info.render_settings"
    bl_label = "Render Settings"
    
    room_builder_tabs = bpy.props.EnumProperty(name="Room Builder Tabs",
        items=[('MAIN',"Main Settings","Displays the Main Rendering Options"),
               ('LIGHTING',"Lighting","Library of Room Assets"),
               ('2D',"2D Views","Creates 2D Views For your Room")],
        default='MAIN')    
    
    def execute(self, context):
        return {'FINISHED'}
    
    def check(self,context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        rd = scene.render
        cycles = scene.cycles
        image_settings = rd.image_settings
#         ui = context.scene.mv.ui
        
        rl = rd.layers.active
        linestyle = rl.freestyle_settings.linesets[0].linestyle
        
        box = layout.box()
        row = box.row(align=True)
        if rd.has_multiple_engines:
            row.prop(rd, "engine", text="Rendering Engine")               
        
        row = box.row()
        row.prop(cycles, "device", text="CPU")
        
        row = box.row(align=True)
        row.label(text="Render Size:",icon='STICKY_UVS_VERT')        
        row.prop(rd, "resolution_x", text="X")
        row.prop(rd, "resolution_y", text="Y")
        row = box.row(align=True)
        row.label("Resolution Percentage:")
        row.prop(rd, "resolution_percentage", text="")
        
#         if ui.render_type_tabs == 'PRR':
        row = box.row()
        row.label(text="Rendering Quality:",icon='IMAGE_COL')
        row.prop(scene.cycles,"samples",text='Passes')
        row = box.row()
        row.label(text="Image Format:",icon='IMAGE_DATA')
        row.prop(image_settings,"file_format",text="")
        row = box.row()
        row.label(text="Display Mode:",icon='RENDER_RESULT')
        row.prop(rd,"display_mode",text="")
        row = box.row()
        row.label(text="Use Transparent Film:",icon='SEQUENCE')
        row.prop(scene.cycles,"film_transparent",text='')

        row = box.row()
        row.prop(rd, "use_freestyle", text="Use Freestyle")       
        if rd.use_freestyle: 
            row = box.row()
            row.prop(linestyle, "color", text="Line Color")
            row = box.row()
            row.prop(bpy.data.worlds[0], "horizon_color", text="Background Color")        
        
def register():
    if hasattr(bpy.types, 'INFO_HT_header'):
        bpy.utils.unregister_class(bpy.types.INFO_HT_header)    
            
    bpy.utils.register_class(INFO_HT_header)
    bpy.utils.register_class(INFO_MT_menus)
    bpy.utils.register_class(INFO_MT_file)
    bpy.utils.register_class(INFO_MT_edit)
    bpy.utils.register_class(INFO_MT_rendering)
    bpy.utils.register_class(OPS_render_settings)
    
def unregister():
    pass        
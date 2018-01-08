import bpy

from . import space_info
from . import space_view3d
from . import object_properties_panel

def register():
	space_info.register()
	space_view3d.register()
	object_properties_panel.register()
	
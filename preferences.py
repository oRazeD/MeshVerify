import bpy
from bpy.props import StringProperty, IntProperty, PointerProperty, BoolProperty
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu


class MESHVFY_MT_presets(Menu):
    bl_label = ""
    preset_subdir = "meshVerify"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class MESHVFY_PT_presets(PresetPanel, Panel):
    bl_label = 'MESHVFY Presets'
    preset_subdir = 'mesh_vfy'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'mesh_vfy.preset_add'


class MESHVFY_OT_add_preset(AddPresetBase, bpy.types.Operator):
    bl_idname = "mesh_vfy.preset_add"
    bl_label = "Add a new preset"
    preset_menu = "MESHVFY_MT_presets"

    # Variable used for all preset values
    preset_defines = ["mesh_vfy_prefs = bpy.context.scene.mesh_vfy_prefs"]

    # Properties to store in the preset
    preset_values = [
        "mesh_vfy_prefs.use_selected_only",

        "mesh_vfy_prefs.count_tris",
        "mesh_vfy_prefs.count_quads",
        "mesh_vfy_prefs.count_ngons",
        "mesh_vfy_prefs.count_tris_result",
        "mesh_vfy_prefs.count_quads_result",
        "mesh_vfy_prefs.count_ngons_result"]

    # Where to store the preset
    preset_subdir = "mesh_vfy"


##################################
#   Property Groups
##################################


class MESHVFY_property_group(bpy.types.PropertyGroup):
    def lightmap_suffix_update(self, context):
        if not context.scene.mesh_vfy_prefs.lightmap_suffix:
            context.scene.mesh_vfy_prefs.lightmap_suffix = "_lm"

    verify_mesh_ran: BoolProperty(default = False)

    use_selected_only: BoolProperty(name = 'Run on Selected Only', default = True)

    count_tris: BoolProperty(name = 'Tris', default = True)
    count_quads: BoolProperty(name = 'Quads', default = True)
    count_ngons: BoolProperty(name = 'nGons', default = True)
    count_tris_result: IntProperty(name = '', default = 0)
    count_quads_result: IntProperty(name = '', default = 0)
    count_ngons_result: IntProperty(name = '', default = 0)

    count_n_poles: BoolProperty(name = 'N-Poles', default = False)
    count_e_poles: BoolProperty(name = 'E-Poles', default = False)
    count_n_poles_result: IntProperty(name = '', default = 0)
    count_e_poles_result: IntProperty(name = '', default = 0)

    tforms_applied: BoolProperty(name = 'Transforms Applied (Rot & Scale)', default = True)
    tforms_applied_result: BoolProperty(name = '', default = True)
    tforms_applied_amount: IntProperty(name = "", default = 0)

    seams_match_smoothing: BoolProperty(name = 'Seams match Smoothing (Sharps)', default = True)
    seams_match_smoothing_result: BoolProperty(name = '', default = False)

    manifold_meshes: BoolProperty(name = 'Meshes are Manifold', default = True)
    manifold_loose_wire_result: BoolProperty(name = '', default = False)
    manifold_double_faces_result: BoolProperty(name = '', default = False)
    manifold_airtight_result: BoolProperty(name = '', default = True)

    zeroed_tforms: BoolProperty(name = 'Origins at 0,0,0', default = False)
    zeroed_tforms_result: BoolProperty(name = '', default = True)
    zeroed_tforms_amount: IntProperty(name = '', default = 0)

    correct_normal_orient: BoolProperty(name = 'Correct Normal Orientation', default = True)
    correct_normal_orient_result: BoolProperty(name = '', default = True)
    correct_normal_orient_amount: IntProperty(name = '', default = 0)

    flipped_uvs: BoolProperty(name = 'No Flipped UVs', default = False)
    flipped_uvs_result: BoolProperty(name = '', default = False)
    flipped_uvs_amount: IntProperty(name = "", default = 0)

    object_prefix: StringProperty(name = "",
                                  description = "Define the prefix to look for when searching through objects",
                                  default = "")

    object_suffix: StringProperty(name = "",
                                  description = "Define the suffix to look for when searching through objects",
                                  default = "")

    lightmap_suffix: StringProperty(name = "",
                                    description = "Define the suffix to look for when searching for lightmap UVS",
                                    default = "_lm",
                                    update = lightmap_suffix_update)

    optimal_uv_usage: IntProperty(name = "",
                                  description = "Define the value for what you think optimal UV space usage is in %",
                                  default = 70,
                                  min = 0,
                                  max = 100,
                                  subtype = 'PERCENTAGE')

    ob_list_range: IntProperty(name = "",
                               description = "",
                               default = 5,
                               min = 1,
                               max = 250)

    is_ascending: BoolProperty(name = '', default = True)

    use_visible_only: BoolProperty(name = 'Show Visible Only')


##################################
#   REGISTRATION
##################################


classes = (MESHVFY_MT_presets,
           MESHVFY_PT_presets,
           MESHVFY_OT_add_preset,
           MESHVFY_property_group)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mesh_vfy_prefs = PointerProperty(type = MESHVFY_property_group)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.mesh_vfy_prefs


# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
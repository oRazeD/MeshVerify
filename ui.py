import bpy
from bpy.types import Panel
import os
import bpy.utils.previews
from .operators import convert_number


##############################
#   UI
##############################


class PanelInfo:
    bl_category = 'Mesh Verify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class MESHVFY_PT_run_panel(PanelInfo, Panel):
    bl_label = 'Verify Mesh'

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout

        pcoll = preview_collections["main"]

        msh_verify_logo = pcoll["msh_verify_logo"]

        col = layout.column(align = True)
        row = col.row(align = True)
        row.scale_y = 1.6
        row.operator("mesh_vfy.verify_mesh", icon_value=msh_verify_logo.icon_id)

        box = col.box()
        box.prop(mesh_vfy_prefs, 'use_selected_only')


class MESHVFY_PT_configure_object_checks(PanelInfo, Panel):
    bl_label = 'Object Integrity Checks'
    bl_parent_id = "MESHVFY_PT_run_panel"

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout

        col = layout.column()
        split = col.split()

        col_title = split.column()
        col_title.label(text = "   Counters")

        col_left = split.column()
        col_left.prop(mesh_vfy_prefs, 'count_tris')
        col_left.prop(mesh_vfy_prefs, 'count_quads')
        col_left.prop(mesh_vfy_prefs, 'count_ngons')


        col_right = split.column()
        col_right.prop(mesh_vfy_prefs, 'count_n_poles')
        col_right.prop(mesh_vfy_prefs, 'count_e_poles')

        col = layout.column()
        col.prop(mesh_vfy_prefs, 'tforms_applied')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'seams_match_smoothing')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'manifold_meshes')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'zeroed_tforms')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'Origins within Bounding Box')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'Correct Normal Orientation')
        col.separator(factor=.25)

        split = col.split(factor=.7)
        col_left = split.column()
        col_right = split.column()
        col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'Objects contain Prefix:')
        col_right.prop(mesh_vfy_prefs, 'object_prefix')

        col_left.separator(factor=.25)
        col_right.separator(factor=.25)
        col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'Objects contain Suffix:')
        col_right.prop(mesh_vfy_prefs, 'object_suffix')


class MESHVFY_PT_configure_uv_checks(PanelInfo, Panel):
    bl_label = 'UV Integrity Checks'
    bl_parent_id = "MESHVFY_PT_run_panel"

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout

        col = layout.column()

        col.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'No Overlapping UVs')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'flipped_uvs')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'Consistent Texel Density')
        col.separator(factor=.25)

        split = col.split(factor=.7)
        col_left = split.column()
        col_right = split.column()

        col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'Optimal UV Usage:')
        col_right.prop(mesh_vfy_prefs, 'optimal_uv_usage')

        split = col.split(factor=.7)
        col_left = split.column()
        col_right = split.column()
        
        col_left.separator(factor=.25)
        col_right.separator(factor=.25)
        col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = 'Lightmap UVs Present:')
        col_right.prop(mesh_vfy_prefs, 'lightmap_suffix')


class MESHVFY_PT_results(PanelInfo, Panel):
    bl_label = 'Latest Run Results'
    bl_parent_id = "MESHVFY_PT_run_panel"

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout

        if mesh_vfy_prefs.verify_mesh_ran:
            if mesh_vfy_prefs.count_tris or mesh_vfy_prefs.count_quads or mesh_vfy_prefs.count_ngons:
                box = layout.box()
                row = box.row(align = True)

                if mesh_vfy_prefs.count_tris:
                    row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_tris_result)}", icon = 'OUTLINER_DATA_MESH')

                if mesh_vfy_prefs.count_quads:
                    row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_quads_result)}", icon = 'MATPLANE')

                if mesh_vfy_prefs.count_ngons:
                    row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_ngons_result)}", icon = 'SEQ_CHROMA_SCOPE')

            if mesh_vfy_prefs.tforms_applied:
                if not mesh_vfy_prefs.tforms_applied_result:
                    box = layout.box()
                    row = box.row()

                    row.label(text = f"[{mesh_vfy_prefs.tforms_applied_amount}] Transforms are not Applied", icon = "ERROR")

                    row.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')

            if mesh_vfy_prefs.seams_match_smoothing:
                if not mesh_vfy_prefs.seams_match_smoothing_result:
                    box = layout.box()
                    row = box.row()

                    row.label(text = "Seams don't Match Smoothing", icon = "ERROR")

                    row.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')

            if mesh_vfy_prefs.zeroed_tforms:
                if not mesh_vfy_prefs.zeroed_tforms_result:
                    box = layout.box()
                    row = box.row()

                    row.label(text = f"[{mesh_vfy_prefs.zeroed_tforms_amount}] Origin not at 0,0,0", icon = "ERROR")

            if mesh_vfy_prefs.manifold_meshes:
                if mesh_vfy_prefs.manifold_loose_wire_result or mesh_vfy_prefs.manifold_double_faces_result or not mesh_vfy_prefs.manifold_airtight_result:
                    box = layout.box()
                    row = box.row()

                    row.label(text = "Meshes are Not Manifold:", icon = "ERROR")
                    
                    row = box.row()

                    if mesh_vfy_prefs.manifold_loose_wire_result:
                        box_inner = row.box()
                        box_inner.label(text = "    - Loose vertices or wire edges that")
                        row_inner = box_inner.row()
                        row_inner.label(text = "    don't make up a polygon detected")
                        row_inner.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')

                        row = box.row()

                    if mesh_vfy_prefs.manifold_double_faces_result:
                        box_inner = row.box()
                        box_inner.label(text = "    - Multi-faced/sided geometry detected")
                        row_inner = box_inner.row()
                        row_inner.label(text = "    (edges that make up 3+ faces)")
                        row_inner.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')

                        row = box.row()

                    if not mesh_vfy_prefs.manifold_airtight_result:
                        box_inner = row.box()
                        box_inner.label(text = "    - Non-Airtight geometry that contain")
                        row_inner = box_inner.row()
                        row_inner.label(text = "    gaps in your meshes detected")
                        row_inner.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')
                
            if mesh_vfy_prefs.flipped_uvs:
                if mesh_vfy_prefs.flipped_uvs_result:
                    box = layout.box()
                    row = box.row()
                    
                    row.label(text = f"[{mesh_vfy_prefs.flipped_uvs_amount}] Objects with Possible Flipped Detected", icon = "ERROR")
        else:
            row = layout.row()
            row.label(text = "No Results to Show Just Yet.", icon = "INFO")


class MESHVFY_PT_scene_list(PanelInfo, Panel):
    bl_label = 'View Layer Objects List'

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(mesh_vfy_prefs, 'ob_list_range', text = 'List Range')
        layout.prop(mesh_vfy_prefs, 'use_visible_only')


class MESHVFY_PT_objects_list(PanelInfo, Panel):
    bl_label = 'Objects List'
    bl_parent_id = "MESHVFY_PT_scene_list"
    
    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs
        
        object_dict = {}

        for ob in context.view_layer.objects:
            if ob.type == 'MESH':
                if mesh_vfy_prefs.use_visible_only:
                    if ob.visible_get():
                        object_dict[ob] = len(ob.data.polygons)
                else:
                    object_dict[ob] = len(ob.data.polygons)

        layout = self.layout

        col = layout.column(align = True)
        split = col.split(factor=.6, align = True)
        col_left = split.column(align = True)
        col_right = split.column(align = True)

        col_left.label(text = 'Object Name')
        col_right.prop(mesh_vfy_prefs, 'is_ascending', text = 'Polygons', icon = 'SORT_ASC' if mesh_vfy_prefs.is_ascending else 'SORT_DESC', invert_checkbox = True)

        if object_dict:
            list_range = 0

            for ob in sorted(object_dict.items(), key=lambda x:x[1], reverse = mesh_vfy_prefs.is_ascending):
                list_range += 1

                if list_range <= mesh_vfy_prefs.ob_list_range:
                    col_left_box = col_left.box()
                    row = col_left_box.row()
                    row.operator("mesh_vfy.select_mesh", text = '', icon = 'RESTRICT_SELECT_OFF').select_mesh_name = ob[0].name
                    row.label(text = str(ob[0].name))

                    col_right_box = col_right.box()
                    col_right_box.label(text = str(ob[1]))
        else:
            box = col.box()
            box.label(text = "No Mesh Objects are in the scene.", icon = "INFO")


##############################
#   REGISTRATION
##############################


# We can store multiple preview collections here,
# however in this example we only store "main"
preview_collections = {}

classes = (MESHVFY_PT_run_panel,
           MESHVFY_PT_configure_object_checks,
           MESHVFY_PT_configure_uv_checks,
           MESHVFY_PT_results,
           MESHVFY_PT_scene_list,
           MESHVFY_PT_objects_list)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    pcoll.load("msh_verify_logo", os.path.join(my_icons_dir, "msh_verify_logo.png"), 'IMAGE')

    preview_collections["main"] = pcoll

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    preview_collections.clear()


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
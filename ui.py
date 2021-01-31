import bpy
from bpy.types import Panel
import os
import bpy.utils.previews
from .operators import convert_number
from .preferences import MESHVFY_PT_presets


##############################
#   UI
##############################


class PanelInfo:
    bl_category = 'Mesh Verify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class MESHVFY_PT_run_panel(PanelInfo, Panel):
    bl_label = 'Verify Mesh'

    def draw_header_preset(self, context):
        MESHVFY_PT_presets.draw_panel_header(self.layout)

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout

        col = layout.column(align = True)
        row = col.row(align = True)
        row.scale_y = 1.6
        row.operator("mesh_vfy.verify_mesh", icon_value=preview_collections["main"]["msh_verify_logo"].icon_id)

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
        col.prop(mesh_vfy_prefs, 'flipped_uvs', text = '_Origins within Bounding Box')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'correct_normal_orient')
        col.separator(factor=.25)

        split = col.split(factor=.7)
        col_left = split.column()
        col_right = split.column()
        col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = '_Objects contain Prefix:')
        col_right.prop(mesh_vfy_prefs, 'object_prefix')

        col_left.separator(factor=.25)
        col_right.separator(factor=.25)
        col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = '_Objects contain Suffix:')
        col_right.prop(mesh_vfy_prefs, 'object_suffix')


class MESHVFY_PT_configure_uv_checks(PanelInfo, Panel):
    bl_label = 'UV Integrity Checks'
    bl_parent_id = "MESHVFY_PT_run_panel"

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout

        col = layout.column()

        col.prop(mesh_vfy_prefs, 'flipped_uvs', text = '_No Overlapping UVs')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'flipped_uvs')
        col.separator(factor=.25)
        col.prop(mesh_vfy_prefs, 'flipped_uvs', text = '_Consistent Texel Density')
        col.separator(factor=.25)

        split = col.split(factor=.7)
        col_left = split.column()
        col_right = split.column()

        col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = '_Optimal UV Usage:')
        col_right.prop(mesh_vfy_prefs, 'optimal_uv_usage')

        #split = col.split(factor=.7)
        #col_left = split.column()
        #col_right = split.column()
        #
        #col_left.separator(factor=.25)
        #col_right.separator(factor=.25)
        #col_left.prop(mesh_vfy_prefs, 'flipped_uvs', text = '_Lightmap UVs Present:')
        #col_right.prop(mesh_vfy_prefs, 'lightmap_suffix')


class MESHVFY_PT_results(PanelInfo, Panel):
    bl_label = 'Latest Run Results'
    bl_parent_id = "MESHVFY_PT_run_panel"

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout

        if mesh_vfy_prefs.verify_mesh_ran:
            if mesh_vfy_prefs.count_tris or mesh_vfy_prefs.count_quads or mesh_vfy_prefs.count_ngons or mesh_vfy_prefs.count_e_poles or mesh_vfy_prefs.count_n_poles:
                box = layout.box()
                col = box.column(align = True)
                col.scale_y = 1.05

                if mesh_vfy_prefs.count_tris or mesh_vfy_prefs.count_quads or mesh_vfy_prefs.count_ngons:
                    row = col.row(align = True)

                    if mesh_vfy_prefs.count_tris:
                        row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_tris_result)}", icon_value = preview_collections["main"]["tri_icon_32"].icon_id)

                    if mesh_vfy_prefs.count_quads:
                        row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_quads_result)}", icon_value = preview_collections["main"]["quad_icon_32"].icon_id)

                    if mesh_vfy_prefs.count_ngons:
                        row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_ngons_result)}", icon_value = preview_collections["main"]["ngon_icon_32"].icon_id)

                if mesh_vfy_prefs.count_e_poles or mesh_vfy_prefs.count_n_poles:
                    row = col.row(align = True)

                    if mesh_vfy_prefs.count_n_poles:
                        row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_n_poles_result)}", icon_value = preview_collections["main"]["npole_icon_32"].icon_id)

                    if mesh_vfy_prefs.count_e_poles:
                        row.operator("mesh_vfy.verify_mesh", text = f"{convert_number(mesh_vfy_prefs.count_e_poles_result)}", icon_value = preview_collections["main"]["epole_icon_32"].icon_id)

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

                    row.label(text = f"[{mesh_vfy_prefs.zeroed_tforms_amount}] Origins not at 0,0,0", icon = "ERROR")

            if mesh_vfy_prefs.manifold_meshes:
                if mesh_vfy_prefs.manifold_loose_wire_result or mesh_vfy_prefs.manifold_double_faces_result or not mesh_vfy_prefs.manifold_airtight_result:
                    box = layout.box()
                    row = box.row()

                    row.label(text = "Potentially Not Manifold:", icon = "ERROR")
                    
                    row = box.row()

                    if mesh_vfy_prefs.manifold_loose_wire_result:
                        box_inner = row.box()
                        box_inner.label(text = "    - Non-polygonal loose vertices")
                        row_inner = box_inner.row()
                        row_inner.label(text = "    or wire edges detected")
                        row_inner.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')

                        row = box.row()

                    if mesh_vfy_prefs.manifold_double_faces_result:
                        box_inner = row.box()
                        box_inner.label(text = "    - Tri-faced edges detected")
                        row_inner = box_inner.row()
                        row_inner.label(text = "    (edges with 3+ faces)")
                        row_inner.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')

                        row = box.row()

                    if not mesh_vfy_prefs.manifold_airtight_result:
                        box_inner = row.box()
                        box_inner.label(text = "    - Non-Airtight geometry with")
                        row_inner = box_inner.row()
                        row_inner.label(text = "    mesh gaps detected")
                        row_inner.operator("mesh_vfy.verify_mesh", text = '', icon = 'RESTRICT_SELECT_OFF')

            if mesh_vfy_prefs.correct_normal_orient:
                if not mesh_vfy_prefs.correct_normal_orient_result:
                        box = layout.box()
                        row = box.row()

                        row.label(text = f"[{mesh_vfy_prefs.correct_normal_orient_amount}] Incorrect normal orientation", icon = "ERROR")
                
            if mesh_vfy_prefs.flipped_uvs:
                if mesh_vfy_prefs.flipped_uvs_result:
                    box = layout.box()
                    row = box.row()
                    
                    row.label(text = f"[{mesh_vfy_prefs.flipped_uvs_amount}] Potential Flipped UVs", icon = "ERROR")
        else:
            row = layout.row()
            row.label(text = "No Results to Show Just Yet.", icon = "INFO")


class MESHVFY_PT_scene_objects_list(PanelInfo, Panel):
    bl_label = 'View Layer Object Poly List'

    def draw(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(mesh_vfy_prefs, 'ob_list_range', text = 'List Range')
        layout.prop(mesh_vfy_prefs, 'use_visible_only')

        object_dict = {}

        for ob in context.view_layer.objects:
            if ob.type == 'MESH':
                if mesh_vfy_prefs.use_visible_only:
                    if ob.visible_get():
                        object_dict[ob] = len(ob.data.polygons)
                else:
                    object_dict[ob] = len(ob.data.polygons)

        col = layout.column(align = True)
        split = col.split(factor=.65, align = True)
        col_left = split.column(align = True)
        col_right = split.column(align = True)

        col_left.label(text = 'Object Name')
        col_right.prop(mesh_vfy_prefs, 'is_ascending', text = '', icon = 'SORT_ASC' if mesh_vfy_prefs.is_ascending else 'SORT_DESC', invert_checkbox = True)

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


preview_collections = {}

classes = (MESHVFY_PT_run_panel,
           MESHVFY_PT_configure_object_checks,
           MESHVFY_PT_configure_uv_checks,
           MESHVFY_PT_results,
           MESHVFY_PT_scene_objects_list)

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
    pcoll.load("tri_icon_32", os.path.join(my_icons_dir, "tri_icon_32.png"), 'IMAGE')
    pcoll.load("quad_icon_32", os.path.join(my_icons_dir, "quad_icon_32.png"), 'IMAGE')
    pcoll.load("ngon_icon_32", os.path.join(my_icons_dir, "ngon_icon_32.png"), 'IMAGE')
    pcoll.load("npole_icon_32", os.path.join(my_icons_dir, "npole_icon_32.png"), 'IMAGE')
    pcoll.load("epole_icon_32", os.path.join(my_icons_dir, "epole_icon_32.png"), 'IMAGE')
    
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
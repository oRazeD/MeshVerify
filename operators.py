import bpy, bmesh, array
from mathutils import Vector
from bpy.props import StringProperty


##############################
#   OPERATORS
##############################


def convert_number(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M'][magnitude])


class MESHVFY_OT_select_mesh(bpy.types.Operator):
    bl_idname = "mesh_vfy.select_mesh"
    bl_label = "Select Mesh"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    select_mesh_name: StringProperty(name = "", default = "")

    def execute(self, context):
        if context.object:
            bpy.ops.object.mode_set(mode="OBJECT")

        for ob in context.scene.objects:
            if ob.select_set:
                ob.select_set(False)

            if ob.name == self.select_mesh_name:
                ob.select_set(True)
                context.view_layer.objects.active = ob
        return{'FINISHED'}


class MESHVFY_OT_verify_mesh(bpy.types.Operator):
    bl_idname = "mesh_vfy.verify_mesh"
    bl_label = "Verify Meshes"
    bl_description = "Verify that your meshes are set up properly based on an array of options"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects

    def zeroed_properties(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        mesh_vfy_prefs.count_tris_result = 0
        mesh_vfy_prefs.count_quads_result = 0
        mesh_vfy_prefs.count_ngons_result = 0

        mesh_vfy_prefs.count_n_poles_result = 0
        mesh_vfy_prefs.count_e_poles_result = 0

        mesh_vfy_prefs.tforms_applied_result = True
        mesh_vfy_prefs.tforms_applied_amount = 0

        mesh_vfy_prefs.seams_match_smoothing_result = True

        mesh_vfy_prefs.manifold_loose_wire_result = False
        mesh_vfy_prefs.manifold_double_faces_result = False
        mesh_vfy_prefs.manifold_airtight_result = True

        mesh_vfy_prefs.zeroed_tforms_result = True
        mesh_vfy_prefs.zeroed_tforms_amount = 0

        mesh_vfy_prefs.flipped_uvs_result = False
        mesh_vfy_prefs.flipped_uvs_amount = 0

        mesh_vfy_prefs.correct_normal_orient_result = True
        mesh_vfy_prefs.correct_normal_orient_amount = 0

    def mesh_vfy(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        # Counters
        if mesh_vfy_prefs.count_tris or mesh_vfy_prefs.count_quads or mesh_vfy_prefs.count_ngons:
            for loop in self.ob.data.polygons:
                count = loop.loop_total

                # Tris
                if count == 3 and mesh_vfy_prefs.count_tris:
                    mesh_vfy_prefs.count_tris_result += 1

                # Quads
                elif count == 4 and mesh_vfy_prefs.count_quads:
                    mesh_vfy_prefs.count_quads_result += 1

                # Ngons
                elif count > 4 and mesh_vfy_prefs.count_ngons:
                    mesh_vfy_prefs.count_ngons_result += 1

        if mesh_vfy_prefs.count_e_poles or mesh_vfy_prefs.count_n_poles:
            self.bm.from_mesh(self.ob.data)

            for v in self.bm.verts:
                # N-Poles
                if len(v.link_edges) >= 5 and mesh_vfy_prefs.count_n_poles:
                    mesh_vfy_prefs.count_n_poles_result += 1

                # E-Poles
                elif len(v.link_edges) == 3 and mesh_vfy_prefs.count_e_poles:
                    mesh_vfy_prefs.count_e_poles_result += 1

        # Transforms Applied
        if mesh_vfy_prefs.tforms_applied:
            if self.ob.scale[0] != 1 or self.ob.scale[1] != 1 or self.ob.scale[2] != 1 or self.ob.rotation_euler[0] != 0 or self.ob.rotation_euler[1] != 0 or self.ob.rotation_euler[2] != 0:
                mesh_vfy_prefs.tforms_applied_result = False
                mesh_vfy_prefs.tforms_applied_amount += 1

        # Seams Match Smoothing    
        if mesh_vfy_prefs.seams_match_smoothing_result:
            if mesh_vfy_prefs.seams_match_smoothing:
                for edge in self.ob.data.edges:
                    if edge.use_edge_sharp or edge.use_seam:
                        if not edge.use_edge_sharp or not edge.use_seam:
                            mesh_vfy_prefs.seams_match_smoothing_result = False
                            break

        # Zeroed Transforms
        if mesh_vfy_prefs.zeroed_tforms:
            if self.ob.location[0] != 0 or self.ob.location[1] != 0 or self.ob.location[2] != 0:
                mesh_vfy_prefs.zeroed_tforms_result = False
                mesh_vfy_prefs.zeroed_tforms_amount += 1

        # Correct Normal Orientation
        if mesh_vfy_prefs.correct_normal_orient:
            self.bm.from_mesh(self.ob.data)

            for edge in self.bm.edges:
                if edge.select:
                    if len(edge.link_faces) == 2 and not edge.is_contiguous:
                        mesh_vfy_prefs.correct_normal_orient_result = False
                        mesh_vfy_prefs.correct_normal_orient_amount += 1
                        break
        
        # Flipped UVs
        if mesh_vfy_prefs.flipped_uvs:
            for poly in self.ob.data.polygons:
                # Calculate uv differences between current and next face vertex for whole polygon	  
                diffs = []
                for l_i in poly.loop_indices:

                    next_l = l_i+1 if l_i < poly.loop_start + poly.loop_total - 1 else poly.loop_start
                    
                    next_v_uv = self.ob.data.uv_layers.active.data[next_l].uv
                    v_uv = self.ob.data.uv_layers.active.data[l_i].uv
                    
                    diffs.append((next_v_uv - v_uv).to_3d())

                # Go through all uv differences and calculate cross product between current and next.
                # cross product gives us normal of the triangle. That normal is then used in dot product
                # with up vector (0,0,1). If result is negative we have found a flipped part of the polygon.
                for i, diff in enumerate(diffs):
                    if i == len(diffs)-1:
                        break
                    
                    # When we find a partially flipped polygon we select it and finish search
                    if diffs[i].cross(diffs[i+1]) @ Vector((0,0,1)) <= 0:
                        mesh_vfy_prefs.flipped_uvs_result = True
                        mesh_vfy_prefs.flipped_uvs_amount += 1
                        break

        # EDIT MODE OPERATIONS
        
        # Manifold Meshes
        if mesh_vfy_prefs.manifold_meshes:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

            # Loose/Wire Geometry
            if not mesh_vfy_prefs.manifold_loose_wire_result:
                bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=True)
                if self.ob.data.total_vert_sel:
                    mesh_vfy_prefs.manifold_loose_wire_result = True

            # Multi-Face Geometry
            if not mesh_vfy_prefs.manifold_double_faces_result:
                bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=False, use_multi_face=True, use_non_contiguous=False, use_verts=False)
                if self.ob.data.total_vert_sel:
                    mesh_vfy_prefs.manifold_double_faces_result = True
            
            # Non-Airtight Geometry
            if mesh_vfy_prefs.manifold_airtight_result:
                bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
                if self.ob.data.total_vert_sel:
                    mesh_vfy_prefs.manifold_airtight_result = False

            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode="OBJECT")

    def execute(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        # Checks before running. If there is an active object but nothing is selected, select the Active Object
        if context.selected_objects and not context.active_object:
            context.view_layer.objects.active = context.selected_objects[0]

        if mesh_vfy_prefs.use_selected_only and not context.selected_objects:
            if context.active_object:
                bpy.data.objects[context.active_object.name].select_set(True)
            else:
                self.report({'ERROR'}, "You have 'Use Selected Only' turned on, but nothing is selected. Aborting...")
                return{'FINISHED'}

        # Work only in Object Mode. If there is no active object, select one. Also save original Context mode
        if context.active_object:
            mode_callback = context.active_object.mode

            bpy.ops.object.mode_set(mode="OBJECT")
        else:
            context.view_layer.objects.active = context.view_layer.objects[0]

        # Check to show results
        mesh_vfy_prefs.verify_mesh_ran = True

        # Reset Variables/Properties (Default value is based on "healthy" state)
        # Example: 'tforms_applied_result=True' because you would want them applied but 'flipped_uvs_result=False' because you wouldn't want any UVs flipped)
        self.zeroed_properties(context)

        #del bpy.context.scene['mesh_vfy_prefs']
        
        # Create a global bmesh to slam dunk meshes into
        self.bm = bmesh.new()

        to_be_verified_objects = context.selected_objects if mesh_vfy_prefs.use_selected_only else context.view_layer.objects

        for self.ob in to_be_verified_objects:
            if self.ob.type == 'MESH':
                self.mesh_vfy(context)

        # Reset context mode
        if 'mode_callback' in locals():
            bpy.ops.object.mode_set(mode=mode_callback)
        return{'FINISHED'}


##############################
#   REGISTRATION    
##############################


def register():
    bpy.utils.register_class(MESHVFY_OT_verify_mesh)
    bpy.utils.register_class(MESHVFY_OT_select_mesh)

def unregister():
    bpy.utils.unregister_class(MESHVFY_OT_verify_mesh)
    bpy.utils.unregister_class(MESHVFY_OT_select_mesh)


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
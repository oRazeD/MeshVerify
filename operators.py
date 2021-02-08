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

    def invoke(self, context, event):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        # Checks before running. If there is an active object but nothing is selected, select the Active Object
        if mesh_vfy_prefs.use_selected_only and not context.selected_objects:
            self.report({'ERROR'}, "You have 'Use Selected Only' turned on, but nothing is selected. Aborting...")
            return{'CANCELLED'}

        # Reset Variables/Properties (Default value is based on "healthy" state)
        # Example: 'tforms_applied_result=True' because you would want them applied but 'flipped_uvs_result=False' because you wouldn't want any UVs flipped)
        mesh_vfy_prefs.count_tris_amount = 0
        mesh_vfy_prefs.count_quads_amount = 0
        mesh_vfy_prefs.count_ngons_amount = 0

        mesh_vfy_prefs.count_n_poles_amount = 0
        mesh_vfy_prefs.count_e_poles_amount = 0

        mesh_vfy_prefs.tforms_applied_result = True
        mesh_vfy_prefs.tforms_applied_amount = 0

        mesh_vfy_prefs.seams_match_smoothing_result = True

        mesh_vfy_prefs.manifold_loose_wire_result = False
        mesh_vfy_prefs.manifold_double_faces_result = False
        mesh_vfy_prefs.manifold_airtight_result = True

        mesh_vfy_prefs.zeroed_origins_result = True
        mesh_vfy_prefs.zeroed_origins_amount = 0

        mesh_vfy_prefs.origin_in_bbox_result = True
        mesh_vfy_prefs.origin_in_bbox_amount = 0

        mesh_vfy_prefs.flipped_uvs_result = False
        mesh_vfy_prefs.flipped_uvs_amount = 0

        mesh_vfy_prefs.correct_normal_orient_result = True
        mesh_vfy_prefs.correct_normal_orient_amount = 0

        mesh_vfy_prefs.no_overlapping_verts_result = True
        mesh_vfy_prefs.no_overlapping_verts_amount = 0
        return self.execute(context)
        
    def IsInBoundingVectors(self, vector_check, vector1, vector2):
        # checks if a supplied coordinate if in the bounding box created by vector1 and vector2

        for i in range(0, 3):
            if (vector_check[i] < vector1[i] and vector_check[i] < vector2[i]
                or vector_check[i] > vector1[i] and vector_check[i] > vector2[i]):
                return False
        return True

    def mesh_vfy(self, context):
        mesh_vfy_prefs = context.scene.mesh_vfy_prefs

        # Counters
        if mesh_vfy_prefs.count_tris or mesh_vfy_prefs.count_quads or mesh_vfy_prefs.count_ngons:
            for loop in self.ob.data.polygons:
                count = loop.loop_total

                # Tris
                if mesh_vfy_prefs.count_tris:
                    mesh_vfy_prefs.count_tris_result = True

                    if count == 3:
                        mesh_vfy_prefs.count_tris_amount += 1

                # Quads
                if mesh_vfy_prefs.count_quads:
                    mesh_vfy_prefs.count_quads_result = True

                    if count == 4:
                        mesh_vfy_prefs.count_quads_amount += 1

                # Ngons
                if mesh_vfy_prefs.count_ngons:
                    mesh_vfy_prefs.count_ngons_result = True
                    
                    if count > 4:
                        mesh_vfy_prefs.count_ngons_amount += 1

        if mesh_vfy_prefs.count_e_poles or mesh_vfy_prefs.count_n_poles:
            for v in self.bm.verts:
                # N-Poles
                if mesh_vfy_prefs.count_n_poles:
                    mesh_vfy_prefs.count_n_poles_result = True

                    if len(v.link_edges) == 3:
                        mesh_vfy_prefs.count_n_poles_amount += 1

                # E-Poles
                if mesh_vfy_prefs.count_e_poles:
                    mesh_vfy_prefs.count_e_poles_result = True

                    if len(v.link_edges) >= 5:
                        mesh_vfy_prefs.count_e_poles_amount += 1

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

        # Zeroed Origins
        if mesh_vfy_prefs.zeroed_origins:
            if self.ob.location[0] != 0 or self.ob.location[1] != 0 or self.ob.location[2] != 0:
                mesh_vfy_prefs.zeroed_origins_result = False
                mesh_vfy_prefs.zeroed_origins_amount += 1

        # Origins within Bounding Boxes (can be inaccurate when transforms are unapplied)
        if mesh_vfy_prefs.origin_in_bbox:
            local_bbox_center = 0.125 * sum((Vector(b) for b in self.ob.bound_box), Vector())
            global_bbox_center = self.ob.matrix_world @ local_bbox_center
                    
            vec1 = Vector((-self.ob.dimensions.x / 2 + global_bbox_center[0], -self.ob.dimensions.y / 2 + global_bbox_center[1], -self.ob.dimensions.z / 2 + global_bbox_center[2]))
            vec2 = Vector((self.ob.dimensions.x / 2 + global_bbox_center[0], self.ob.dimensions.y / 2 + global_bbox_center[1], self.ob.dimensions.z / 2 + global_bbox_center[2]))

            if not self.IsInBoundingVectors(self.ob.location, vec1, vec2):
                mesh_vfy_prefs.origin_in_bbox_result = False
                mesh_vfy_prefs.origin_in_bbox_amount += 1

        # Correct Normal Orientations
        if mesh_vfy_prefs.correct_normal_orient:
            incorrect_faces_index = []

            print("")

            for edge in self.bm.edges:
                print(len(edge.link_faces))
                if not edge.link_faces in incorrect_faces_index:
                    if len(edge.link_faces) == 2 and not edge.is_contiguous:

                        incorrect_faces_index.append(edge.link_faces)

                        edge.select = True


                        mesh_vfy_prefs.correct_normal_orient_result = False
                        mesh_vfy_prefs.correct_normal_orient_amount += 1

            print(list(set(incorrect_faces_index)))

            #mesh_vfy_prefs.correct_normal_orient_amount = len(incorrect_faces_index) / 2
        
        # No Overlapping Vertices
        if mesh_vfy_prefs.no_overlapping_verts:
            find_doubles = bmesh.ops.find_doubles(self.bm, verts=self.bm.verts, dist=mesh_vfy_prefs.overlapping_verts_margin)

            doubles_count = [i.index for o in find_doubles["targetmap"].items() for i in o]
            
            if len(doubles_count):
                mesh_vfy_prefs.no_overlapping_verts_result = False
                mesh_vfy_prefs.no_overlapping_verts_amount += len(doubles_count)
        
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

        # Work only in Object Mode. If there is no active object, select one. Also save original Context mode
        if context.active_object:
            mode_callback = context.active_object.mode

            bpy.ops.object.mode_set(mode="OBJECT")
        else:
            context.view_layer.objects.active = context.view_layer.objects[0]

        # Set to true to activate the run results panel
        mesh_vfy_prefs.verify_mesh_ran = True
        
        to_be_verified_objects = context.selected_objects if mesh_vfy_prefs.use_selected_only else context.view_layer.objects

        for self.ob in to_be_verified_objects:
            if self.ob.type == 'MESH':
                self.bm = bmesh.new()
                self.bm.from_mesh(self.ob.data)

                self.mesh_vfy(context)

                self.bm.to_mesh(self.ob.data) 

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
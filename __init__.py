bl_info = {
    "name": "Mesh Verify",
    "description": "Verify that your mesh is set up properly based on an array of options",
    "author": "Ethan Simon-Law",
    "version": (1, 0, 0),
    "blender": (2, 91, 0),
    "tracker_url": "https://discord.com/invite/wHAyVZG",
    "category": "3D View"}


import importlib
import bpy


module_names = ("ui",
                "property",
                "operators")
                
modules = []

for mod in module_names:
    if mod in locals():
        modules.append(importlib.reload(locals()[mod]))
    else:
        modules.append(importlib.import_module(
            "." + mod, package=__package__))


def register():
    for mod in modules:
        mod.register()

def unregister():
    for mod in modules:
        mod.unregister()


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
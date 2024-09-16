bl_info = {
    "name": "TenderRigs",
    "id_name": "TenderRigs",
    "author": "Meku",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > UI > TenderRigs",
    "description": "Script addon to test automatic rig import for Mektools",
    "warning": "warnings are for people not meku",
    "doc_url": "url",
    "category": "TenderRigs",
}

import bpy # type: ignore
import os

# The mapping of racial codes to the corresponding asset files
racial_code_mapping = {
    'c0101': 'Midlander Male',
    'c0201': 'Midlander Female',
    'c0301': 'Highlander Male',
    'c0401': 'Highlander Female',
    'c0501': 'Elezen Male',
    'c0601': 'Elezen Female',
    'c0701': 'Miqote Male',
    'c0801': 'Miqote Female',
    'c0901': 'Roegadyn Male',
    'c1001': 'Roegadyn Female',
    'c1101': 'Lalafell',
    'c1201': 'Lalafell',
    'c1301': 'Aura Male',
    'c1401': 'Aura Female',
    'c1501': 'Hrothgar Male',
    'c1601': 'Hrothgar Female',
    'c1701': 'Viera Male',
    'c1801': 'Viera Female',
}

# # Function to append a collection from an external Blender file
# def append_collection(race_code):
#     race_name = racial_code_mapping.get(race_code, None)
#     if race_name:
#         assets_path = os.path.join(os.path.dirname(__file__), "assets", f"{race_name}.blend")
#         if os.path.exists(assets_path):
#             collection_name = race_name
#             with bpy.data.libraries.load(assets_path, link=False) as (data_from, data_to):
#                 if collection_name in data_from.collections:
#                     data_to.collections.append(collection_name)
#                     bpy.context.scene.collection.children.link(bpy.data.collections[collection_name])
#                     return bpy.data.collections[collection_name]
#     return None

# Function to append a collection from a Blender file
def append_race_collection(race_code):
    # Define the path to the assets folder (where the Blender files are stored)
    assets_folder = os.path.join(bpy.path.abspath("//"), "assets")
    
    # Create the name of the Blender file based on the race_code
    race_file_name = f"{race_code}.blend"
    race_file_path = os.path.join(assets_folder, race_file_name)
    
    # Check if the Blender file exists
    if not os.path.exists(race_file_path):
        print(f"Error: The file {race_file_path} does not exist.")
        return
    
    # Path to the collection within the Blender file (assuming the collection name matches the file name)
    collection_name = race_code  # Collection name is the same as the race code
    
    # Define the full path to the collection in the Blender file
    collection_path = os.path.join(race_file_path, "Collection", collection_name)
    
    # Append the collection
    bpy.ops.wm.append(
        filepath=collection_path,
        directory=os.path.join(race_file_path, "Collection"),
        filename=collection_name
    )
    
    print(f"Appended collection {collection_name} from {race_file_path}")
    return {'FINISHED'}


# Function to handle Viera ear bones
def handle_viera_ears(armature, viera_object_name):
    # Get the last 4 characters of the object's name (e.g., z0001)
    ear_code = viera_object_name[-5:-1]
    
    # Define bone prefixes to keep and remove
    keep_bones = [f"zera_{ear_code}"]
    remove_bones = [f"zerb_{ear_code}", f"zerc_{ear_code}", f"zerd_{ear_code}"]

    # Remove the undesired bones from the armature
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in armature.data.edit_bones:
        if any(rb in bone.name for rb in remove_bones):
            armature.data.edit_bones.remove(bone)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return keep_bones

# Operator for appending MekRig
class OBJECT_OT_append_mekrig(bpy.types.Operator):
    bl_idname = "object.append_mekrig"
    bl_label = "Append MekRig"
    
    def execute(self, context):
        imported_objects = [obj for obj in context.selected_objects if "_fac" in obj.name]
        
        if not imported_objects:
            self.report({'ERROR'}, "No FBX Imported Objects with '_fac' found.")
            return {'CANCELLED'}
        
        armature = None
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE' and obj.name == "n_root":
                armature = obj
                break
        
        if not armature:
            self.report({'ERROR'}, "No 'n_root' armature found.")
            return {'CANCELLED'}
        
        # Rename the selected armature
        armature.name = "source n_root"
        
        # Find the correct race code and append the corresponding collection
        race_code = None
        for obj in imported_objects:
            race_code = obj.name[:5]
            break
        
        appended_collection = append_race_collection(race_code)
        if not appended_collection:
            self.report({'ERROR'}, "No collection found for race code.")
            return {'CANCELLED'}
        
        # Merge hair objects
        hair_objects = [obj for obj in context.selected_objects if "_hir" in obj.name]
        if hair_objects:
            bpy.context.view_layer.objects.active = hair_objects[0]
            bpy.ops.object.join()
            hair_objects[0].name = "hair"
        
        # Add hair vertex groups to a list of bones to not remove
        hair_bone_names = [vg.name for vg in hair_objects[0].vertex_groups]
        
        # Add default bones to remove (populated later)
        remove_default_bones = ["n_throw",
                                "n_hara",
                                "j_kosi",
                                "j_sebo_a",
                                "j_seba_b",
                                "j_mune_l",
                                "j_mune_r",
                                "j_sebo_c",
                                "j_buki_sebo_l",
                                "j_buki_sebo_r",
                                "j_kubi",
                                "j_kao",
                                "j_ago",
                                "j_f_noanim_ago",
                                "j_f_face",
                                "j_f_ago",
                                "j_f_bero_01",
                                "j_f_bero_02",
                                "j_f_bero_03",
                                "j_f_dago",
                                "j_f_dlip_01_l",
                                "j_f_dlip_02_l",
                                "j_f_dlip_01_r",
                                "j_f_dlip_02_r",
                                "j_f_dmlip_01_l",
                                "j_f_dmlip_02_l",
                                "j_f_dmlip_01_r",
                                "j_f_dmlip_02_r",
                                "j_f_hagukidn",
                                "j_f_dhoho_l",
                                "j_f_dhoho_r",
                                "j_f_dmemoto_l",
                                "j_f_dmemoto_r",
                                "j_f_dmiken_l",
                                "j_f_dmiken_r",
                                "j_f_dslip_l",
                                "j_f_dslip_r",
                                "j_f_eye_l",
                                "j_f_eyepuru_l",
                                "j_f_eye_r",
                                "j_f_eyepuru_r",
                                "j_f_eyeprm_01_l",
                                "j_f_eyeprm_02_l",
                                "j_f_irisprm_l",
                                "j_f_noanim_eyesize_l",
                                "j_f_eyeprm_01_r",
                                "j_f_eyeprm_02_r",
                                "j_f_irisprm_r",
                                "j_f_noanim_eyesize_r",
                                "j_f_eyeprmroll_l",
                                "j_f_eyeprmroll_r",
                                "j_f_hagukiup",
                                "j_f_hana_l",
                                "j_f_hana_r",
                                "j_f_hoho_l",
                                "j_f_hoho_r",
                                "j_f_mab_l",
                                "j_f_mabdn_01_l",
                                "j_f_mabdn_02out_l",
                                "j_f_mabdn_03in_l",
                                "j_f_mabup_01_l",
                                "j_f_mabup_02out_l",
                                "j_f_mabup_03in_l",
                                "j_f_mab_r",
                                "j_f_mabdn_01_r",
                                "j_f_mabdn_02out_r",
                                "j_f_mabdn_03in_r",
                                "j_f_mabup_01_r",
                                "j_f_mabup_02out_r",
                                "j_f_mabup_03in_r",
                                "j_f_mayu_l",
                                "j_f_mayu_r",
                                "j_f_miken_01_l",
                                "j_f_miken_02_l",
                                "j_f_miken_01_r",
                                "j_f_miken_02_r",
                                "j_f_mmayu_l",
                                "j_f_mmayu_r",
                                "j_f_shoho_l",
                                "j_f_shoho_r",
                                "j_f_uhana",
                                "j_f_ulip_01_l",
                                "j_f_ulip_02_l",
                                "j_f_ulip_01_r",
                                "j_f_ulip_02_r",
                                "j_f_umlip_01_l",
                                "j_f_umlip_02_l",
                                "j_f_umlip_01_r",
                                "j_f_umlip_02_r",
                                "j_f_uslip_l",
                                "j_f_uslip_r",
                                "j_kami_a",
                                "j_kami_b",
                                "j_kami_f_l",
                                "j_kami_f_r",
                                "j_mimi_l",
                                "n_ear_a_l",
                                "n_ear_b_l",
                                "j_mimi_r",
                                "n_ear_a_r",
                                "n_ear_b_r",
                                "j_sako_l",
                                "j_ude_a_l",
                                "n_kataarmor_l",
                                "j_ude_b_l",
                                "n_hkata_l",
                                "j_te_l",
                                "n_buki_tate_l",
                                "n_hhiji_l",
                                "n_hijisoubi_l",
                                "n_hte_l",
                                "j_hito_a_l",
                                "j_hito_b_l",
                                "j_ko_a_l",
                                "j_ko_b_l",
                                "j_kusu_a_l",
                                "j_kusu_b_l",
                                "j_naka_a_l",
                                "j_naka_b_l",
                                "j_oya_a_l",
                                "j_oya_b_l",
                                "n_buki_l",
                                "j_sako_r",
                                "n_kataarmor_r",
                                "j_ude_a_r",
                                "j_ude_b_r",
                                "n_hkata_r",
                                "j_te_r",
                                "n_buki_tate_r",
                                "n_hhiji_r",
                                "n_hijisoubi_r",
                                "n_hte_r",
                                "j_hito_a_r",
                                "j_hito_b_r",
                                "j_ko_a_r",
                                "j_ko_b_r",
                                "j_kusu_a_r",
                                "j_kusu_b_r",
                                "j_naka_a_r",
                                "j_naka_b_r",
                                "j_oya_a_r",
                                "j_oya_b_r",
                                "n_buki_r",
                                "j_asi_a_l",
                                "j_asi_b_l",
                                "j_asi_c_l",
                                "n_hizasoubi_l",
                                "j_asi_d_l",
                                "j_asi_e_l",
                                "j_asi_a_r",
                                "j_asi_b_r",
                                "j_asi_c_r",
                                "n_hizasoubi_r",
                                "j_asi_d_r",
                                "j_asi_e_r",
                                "j_buki2_kosi_l",
                                "j_buki2_kosi_r",
                                "j_buki_kosi_l",
                                "j_buki_kosi_r",
                                "j_sk_b_a_l",
                                "j_sk_b_b_l",
                                "j_sk_b_c_l",
                                "j_sk_b_a_r",
                                "j_sk_b_b_r",
                                "j_sk_b_c_r",
                                "j_sk_f_a_l",
                                "j_sk_f_b_l",
                                "j_sk_f_c_l",
                                "j_sk_f_a_r",
                                "j_sk_f_b_r",
                                "j_sk_f_c_r",
                                "j_sk_s_a_l",
                                "j_sk_s_b_l",
                                "j_sk_s_c_l",
                                "j_sk_s_a_r",
                                "j_sk_s_b_r",
                                "j_sk_s_c_r",
                                "n_sippo_a",
                                "n_sippo_b",
                                "n_sippo_c",
                                "n_sippo_d",
                                "n_sippo_e"]


        # Special handling for Viera race (race code: c1701 or c1801)
        if race_code in ['c1701', 'c1801']:
            for obj in context.selected_objects:
                if "_zer" in obj.name:
                    keep_bones = handle_viera_ears(armature, obj.name)
                    hair_bone_names.extend(keep_bones)

        # Remove default bones from source armature
        for bone in armature.data.bones:
            if bone.name in remove_default_bones and bone.name not in hair_bone_names:
                armature.data.edit_bones.remove(armature.data.edit_bones[bone.name])
        
        # Merge armature with the new appended one
        appended_armature = appended_collection.objects.get("n_root")
        if appended_armature:
            # Ensure we are in Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Merge the two armatures
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.join()
            
            # Go into Edit Mode and parent hair bones to "mek kao"
            bpy.ops.object.mode_set(mode='EDIT')
            for bone_name in hair_bone_names:
                if bone_name in armature.data.edit_bones:
                    bone = armature.data.edit_bones[bone_name]
                    bone.parent = armature.data.edit_bones.get("mek kao", None)
                    bone.custom_shape = bpy.data.objects.get("cs.hair", None)
                    bone.bone_group = 1  # Bone color (assuming Theme 1 corresponds to group 1)
            
            # Go back to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}

# Panel in the 3D View for the addon
class VIEW3D_PT_mekrig_panel(bpy.types.Panel):
    bl_label = "MekRig Appender"
    bl_idname = "VIEW3D_PT_mekrig_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MekRig"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.append_mekrig")

# Register the addon
def register():
    bpy.utils.register_class(OBJECT_OT_append_mekrig)
    bpy.utils.register_class(VIEW3D_PT_mekrig_panel)

# Unregister the addon
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_append_mekrig)
    bpy.utils.unregister_class(VIEW3D_PT_mekrig_panel)

if __name__ == "__main__":
    register()

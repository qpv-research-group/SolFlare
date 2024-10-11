from solcore import material
from solcore.material_system import create_new_material
import os

def run():

    try:
        MgF2 = material('MgF2_RdeM')()

    except:
        cur_path = cur_path = os.path.dirname(os.path.abspath(__file__))
        create_new_material(
            "Perovskite_CsBr_1p6eV", os.path.join(cur_path, "data/CsBr10p_1to2_n_shifted.txt"), os.path.join(cur_path, "data/CsBr10p_1to2_k_shifted.txt"),
        )
        create_new_material(
            "MgF2_RdeM", os.path.join(cur_path, "data/MgF2_RdeM_n.txt"), os.path.join(cur_path, "data/MgF2_RdeM_k.txt")
        )
        create_new_material(
            "Ag_Jiang", os.path.join(cur_path, "data/Ag_UNSW_n.txt"), os.path.join(cur_path, "data/Ag_UNSW_k.txt")
        )
        print("materials added to database")
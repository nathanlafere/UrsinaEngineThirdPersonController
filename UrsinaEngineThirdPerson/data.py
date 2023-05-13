from ursina import *

ground = ()
player_model = "assets/Jinx.gltf"
player_action_running = "JinxRigAction.1"
player_actions_combo = ("JinxRigAction.1","JinxRigAction.1","JinxRigAction.1")
last_move_button = (0,0) # [0]key [1]time
last_attack_button = (0,0,0) # [0]key [1]time [2]combo len
from ursina import *

ground = Mesh(vertices=[], uvs=[])
player_model = "assets/archer.gltf"
last_move_button = (0,0) # [0]key [1]time
last_attack_button = (0,0,0) # [0]key [1]time [2]combo len
animation_jump = {'rise','falling','land'}
animation_attack = {
    'bow-w': 'attack_forward',
    'bow-s': 'attack_back',
    'bow-d': 'attack_right',
    'bow-a': 'attack_left',
    'sword-w': 'attack_forward',
    'sword-s': 'attack_back',
    'sword-d': 'attack_right',
    'sword-a': 'attack_left'
}

class Character():
    def __init__(self):
        self.str = 6
        self.agi = 1
        self.vit = 1
        self.luk = 5
        self.speed = 4
        self.health = 60

        self.invulnerable = False
        
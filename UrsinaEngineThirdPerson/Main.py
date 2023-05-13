from ursina import *
import data
import enemy
import third_person_controller

app = Ursina()

    
def input(key):
    if key == 'escape':
        quit()

data.ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
Sky()
enemy_01 = enemy.Enemy(actor="assets/Poring.gltf",health=50, rest_time=6, scale=3)
player = third_person_controller.ThirdPersonController(collider="box")

app.run()
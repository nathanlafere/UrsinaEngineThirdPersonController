from ursina import *
import data
import enemy
import portal
import third_person_controller
from panda3d import *

app = Ursina()

    
def input(key):
    if key == 'escape':
        quit()

data.ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
Sky()

poring = load_model("assets/Poring.gltf")
enemy_01 = enemy.Enemy(actor_model="assets/Poring.gltf", scale=2, position=(25,500,10))

ex_portal = portal.Portal(position=(10,0,10),exit_position=(20,0,-20))
player = third_person_controller.ThirdPersonController()
player.collider.visible = True

app.run()
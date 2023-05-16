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

enemy_01 = enemy.Enemy(actor_model="assets/Poring.gltf",health=50, rest_time=6, scale=3, position=(20,500,10))
ex_portal = portal.Portal(position=(10,data.ground.y+2,10),exit_position=(20,0,-20))
player = third_person_controller.ThirdPersonController()


app.run()
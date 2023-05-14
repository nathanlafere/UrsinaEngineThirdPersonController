from ursina import *
import data
import enemy
import third_person_controller
from panda3d import *
from direct.actor.Actor import Actor

app = Ursina()

def update():
    print(actor.getCurrentFrame())

def input(key):
    if key == 'escape':
        quit()

data.ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
Sky()

teste_01 = Entity(position=(10,0,10), scale=2)
actor = Actor("assets/Poring.gltf")
actor.reparentTo(teste_01)
actor.loop("Walk_Action")

enemy_01 = enemy.Enemy(actor_model="assets/Poring.gltf",health=50, rest_time=6, scale=3)
player = third_person_controller.ThirdPersonController(collider="box")

app.run()
from ursina import *
import data
import enemies
import structs
import third_person_controller
import perlin_noise_map
from panda3d import *
import interface

app = Ursina()

def input(key):
    if key == 'escape':
        quit()


Sky()
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=2, position=(25,0,10), experience=25)
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=3, position=(25,0,15), experience=25)
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=4, position=(25,0,20), experience=25)
ex_portal = structs.Portal(position=(10,0,10),exit_position=(20,0,-20), rotation_y=30)
player = third_person_controller.ThirdPersonController()
base_interface = interface.BaseInterface(player)
data.ground = perlin_noise_map.PerlinNoiseMap(player,40)

app.run()
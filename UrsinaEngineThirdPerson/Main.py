from ursina import *
import data
import enemies
import structs
import third_person_controller
import perlin_noise_map
import interface
from ursina.shaders import basic_lighting_shader

app = Ursina()

def input(key):
    if key == 'escape':
        quit()


Sky()
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=2, position=(25,0,10), experience=25, shader=basic_lighting_shader)
enemy_02 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=3, position=(25,0,15), experience=25, shader=basic_lighting_shader)
enemy_03 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=4, position=(25,0,20), experience=25, shader=basic_lighting_shader)
player = third_person_controller.ThirdPersonController()
base_interface = interface.BaseInterface(player)
data.ground = perlin_noise_map.PerlinNoiseMap(player,150,'grass',rendering_distance=30, size_render=40,amp=5)
ex_portal = structs.Portal(position=(0,15),exit_position=(20,15), rotation_y=70, shader=basic_lighting_shader)

app.run()



from ursina import *
import data
import enemies
import structs
import third_person_controller
import perlin_noise_map
import interface

app = Ursina()

def input(key):
    if key == 'escape':
        quit()


Sky()
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=2, position=(25,0,10), experience=25)
enemy_02 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=3, position=(25,0,15), experience=25)
enemy_03 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=4, position=(25,0,20), experience=25)
player = third_person_controller.ThirdPersonController()
base_interface = interface.BaseInterface(player)
data.ground = perlin_noise_map.PerlinNoiseMap(player,80,'grass',rendering_distance=1, size_render=1,amp=8)
ex_portal = structs.Portal(position=(0,15),exit_position=(20,15), rotation_y=70)

app.run()



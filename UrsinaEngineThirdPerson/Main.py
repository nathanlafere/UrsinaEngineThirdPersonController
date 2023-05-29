from ursina import *
import data
import enemies
import structs
import third_person_controller
from perlin_noise import PerlinNoise
from panda3d import *
import itertools

app = Ursina()


    
def input(key):
    if key == 'escape':
        quit()

#data.ground = Entity(model='plane', scale=100, texture='grass', collider='box')
noise = PerlinNoise(octaves=1,seed=1)
terrain_width = 32

for z, x in itertools.product(range(terrain_width), range(terrain_width)):
    y = noise([x/terrain_width, z/terrain_width])*5
    block = Entity(model='plane', position=(x-terrain_width/2,y,z-terrain_width/2), scale=(1,0.1,1))
    block.parent = data.ground
    block.rotation_x = (noise([x/terrain_width, (z-1)/terrain_width])*5 -block.y)*56.4
    block.rotation_z = (noise([(x-1)/terrain_width, z/terrain_width])*5 -block.y)*56.4
data.ground.combine()
data.ground.collider = 'mesh'
data.ground.texture = 'white_cube'

Sky()

enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=2, position=(25,0,10))
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=3, position=(25,0,15))
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=4, position=(25,0,20))
ex_portal = structs.Portal(position=(10,0,10),exit_position=(20,0,-20), rotation_y=30)


player = third_person_controller.ThirdPersonController()
structs.Bridge((40,0,0))

app.run()
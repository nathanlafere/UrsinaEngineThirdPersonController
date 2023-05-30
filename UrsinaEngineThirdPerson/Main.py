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
    if key == 'c':
        data.ground.position += Vec3(1,0,0)

#data.ground = Entity(model='plane', scale=100, texture='grass', collider='box')
noise = PerlinNoise(octaves=3,seed=1)
terrain_width = 30


for z, x in itertools.product(range(terrain_width), range(terrain_width)):
    y = noise([x/terrain_width, z/terrain_width])*5
    data.ground.vertices.extend([
        (x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5),
        (x-terrain_width/2 -0.5, y+ (noise([(x)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5),
        (x-terrain_width/2 -0.5, y, z-terrain_width/2 -0.5),
        (x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z)/terrain_width])*5 -y), z-terrain_width/2 -0.5),
        (x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5),
        (x-terrain_width/2 -0.5, y, z-terrain_width/2 -0.5)])

data.ground = Entity(model=Mesh(vertices=data.ground.vertices, uvs=data.ground.vertices),texture='grass')
data.ground.collider = MeshCollider(data.ground)

Sky()
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=2, position=(25,0,10))
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=3, position=(25,0,15))
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=4, position=(25,0,20))
ex_portal = structs.Portal(position=(10,0,10),exit_position=(20,0,-20), rotation_y=30)


player = third_person_controller.ThirdPersonController()

app.run()
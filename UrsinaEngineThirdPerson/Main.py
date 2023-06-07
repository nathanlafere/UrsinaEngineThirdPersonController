from ursina import *
import data
import enemies
import structs
import third_person_controller
from perlin_noise import PerlinNoise
from panda3d import *
import itertools
import interface

app = Ursina()


def update():
    middle= data.ground.model.vertices[len(data.ground.model.vertices) // 2-120]
    if player.z > middle[2]+8.5:
        move_map('z+')
    if player.z < middle[2]-7.5:
        move_map('z-')
    if player.x > middle[0]+7.5:
        move_map('x+')
    if player.x < middle[0]-8.5:
        move_map('x-')  

def input(key):
    if key == 'escape':
        quit()

def render_map(x,z,index):
    y = noise([x/terrain_width, z/terrain_width])*5
    data.ground.model.vertices.insert(index,(x-terrain_width/2 -0.5, y, z-terrain_width/2 -0.5))
    data.ground.model.vertices.insert(index,(x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5))
    data.ground.model.vertices.insert(index,(x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z)/terrain_width])*5 -y), z-terrain_width/2 -0.5))
    data.ground.model.vertices.insert(index,(x-terrain_width/2 -0.5, y, z-terrain_width/2 -0.5))
    data.ground.model.vertices.insert(index,(x-terrain_width/2 -0.5, y+ (noise([(x)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5))
    data.ground.model.vertices.insert(index,(x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5))


def move_map(direct):
    if direct == 'z+':
        ground_pos = data.ground.model.vertices[-239]
        for c in range(40):
            render_map(c+ground_pos[0]+20.5, ground_pos[2]+20.5, len(data.ground.model.vertices))
        setattr(data.ground, 'model', Mesh(vertices=data.ground.model.vertices[240:],uvs=data.ground.model.vertices[240:]))
    if direct == 'z-':
        ground_pos = data.ground.model.vertices[2]
        for c in range(40):
            render_map(-c+ground_pos[0]+19.5+terrain_width, ground_pos[2]+19.5, 0)
        setattr(data.ground, 'model', Mesh(data.ground.model.vertices[:-240],uvs=data.ground.model.vertices[:-240]))
    if direct == 'x+':
        ground_pos = data.ground.model.vertices[-2]
        for c in range(40):
            render_map(ground_pos[0]+20.5,c+ground_pos[2]-19.5,240*c+240)
            for _ in range(6):
                data.ground.model.vertices.pop(c*240)
        setattr(data.ground, 'model', Mesh(data.ground.model.vertices,uvs=data.ground.model.vertices))
    if direct == 'x-':
        ground_pos = data.ground.model.vertices[2]
        for c in range(40):
            render_map(ground_pos[0]+19.5,c+ground_pos[2]+20.5,c*240)
            for _ in range(6):
                data.ground.model.vertices.pop(240*c+240)
        setattr(data.ground, 'model', Mesh(data.ground.model.vertices,uvs=data.ground.model.vertices))
    data.ground.collider = Mesh(vertices=data.ground.model.vertices)
    

noise = PerlinNoise(octaves=3,seed=1)
terrain_width = 40


for z, x in itertools.product(range(terrain_width), range(terrain_width)):
    y = noise([x/terrain_width, z/terrain_width])*5
    data.ground.vertices.append((x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5))
    data.ground.vertices.append((x-terrain_width/2 -0.5, y+ (noise([(x)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5))
    data.ground.vertices.append((x-terrain_width/2 -0.5, y, z-terrain_width/2 -0.5))
    data.ground.vertices.append((x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z)/terrain_width])*5 -y), z-terrain_width/2 -0.5))
    data.ground.vertices.append((x-terrain_width/2 +0.5, y+ (noise([(x+1)/terrain_width, (z+1)/terrain_width])*5 -y), z-terrain_width/2 +0.5))
    data.ground.vertices.append((x-terrain_width/2 -0.5, y, z-terrain_width/2 -0.5))

data.ground = Entity(model=Mesh(vertices=data.ground.vertices, uvs=data.ground.vertices),texture='white_cube')
data.ground.collider = MeshCollider(data.ground)

Sky()
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=2, position=(25,0,10), experience=25)
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=3, position=(25,0,15), experience=25)
enemy_01 = enemies.Enemy(actor_model="assets/Poring.gltf", scale=4, position=(25,0,20), experience=25)
ex_portal = structs.Portal(position=(10,0,10),exit_position=(20,0,-20), rotation_y=30)
player = third_person_controller.ThirdPersonController()
base_interface = interface.BaseInterface(player)

app.run()
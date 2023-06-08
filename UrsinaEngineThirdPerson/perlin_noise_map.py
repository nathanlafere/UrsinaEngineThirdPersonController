from ursina import *
import itertools
from perlin_noise import PerlinNoise

class PerlinNoiseMap(Entity):
    def __init__(self, player, terrain_width):
        super().__init__()
        self.player = player
        self.terrain_width = terrain_width
        self.noise = PerlinNoise(octaves=3,seed=1)
        self.model = Mesh(vertices=[], uvs=[])
        for z, x in itertools.product(range(terrain_width), range(terrain_width)):
            self.render_map(x,z)
        self.model = Mesh(vertices=self.model.vertices, uvs=self.model.vertices)
        self.texture = 'white_cube'
        self.collider = Mesh(vertices=self.model.vertices)
        self.middle = self.model.vertices[len(self.model.vertices) // 2-120]
        
    def update(self):
        if self.player.z > self.middle[2]+8.5:
            self.move_map('z+')
        if self.player.z < self.middle[2]-7.5:
            self.move_map('z-')
        if self.player.x > self.middle[0]+7.5:
            self.move_map('x+')
        if self.player.x < self.middle[0]-8.5:
            self.move_map('x-')
    
    def move_map(self,direct):
        if direct == 'z+':
            ground_pos = self.model.vertices[-239]
            for c in range(40):
                self.render_map(c+ground_pos[0]+20.5, ground_pos[2]+20.5, len(self.model.vertices))
            setattr(self, 'model', Mesh(vertices=self.model.vertices[240:],uvs=self.model.vertices[240:]))
        if direct == 'z-':
            ground_pos = self.model.vertices[2]
            for c in range(40):
                self.render_map(-c+ground_pos[0]+19.5+self.terrain_width, ground_pos[2]+19.5, 0)
            setattr(self, 'model', Mesh(self.model.vertices[:-240],uvs=self.model.vertices[:-240]))
        if direct == 'x+':
            ground_pos = self.model.vertices[-2]
            for c in range(40):
                self.render_map(ground_pos[0]+20.5,c+ground_pos[2]-19.5,240*c+240)
                for _ in range(6):
                    self.model.vertices.pop(c*240)
            setattr(self, 'model', Mesh(self.model.vertices,uvs=self.model.vertices))
        if direct == 'x-':
            ground_pos = self.model.vertices[2]
            for c in range(40):
                self.render_map(ground_pos[0]+19.5,c+ground_pos[2]+20.5,c*240)
                for _ in range(6):
                    self.model.vertices.pop(240*c+240)
            setattr(self, 'model', Mesh(self.model.vertices,uvs=self.model.vertices))
        self.middle = self.model.vertices[len(self.model.vertices) // 2-120]
        self.collider = Mesh(vertices=self.model.vertices)
    
    def render_map(self,x,z,index= None):
        y = self.noise([x/self.terrain_width, z/self.terrain_width])*5
        if index is None:
            self.model.vertices.append((x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*5 -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.append((x-self.terrain_width/2 -0.5, y+ (self.noise([(x)/self.terrain_width, (z+1)/self.terrain_width])*5 -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.append((x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
            self.model.vertices.append((x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z)/self.terrain_width])*5 -y), z-self.terrain_width/2 -0.5))
            self.model.vertices.append((x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*5 -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.append((x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
        else:
            self.model.vertices.insert(index,(x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*5 -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z)/self.terrain_width])*5 -y), z-self.terrain_width/2 -0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 -0.5, y+ (self.noise([(x)/self.terrain_width, (z+1)/self.terrain_width])*5 -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*5 -y), z-self.terrain_width/2 +0.5))
            self.model.uvs = self.model.vertices
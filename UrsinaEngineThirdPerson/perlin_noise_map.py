from ursina import *
import itertools
from perlin_noise import PerlinNoise
import _thread
from time import sleep


class PerlinNoiseMap(Entity):
    def __init__(self, player, terrain_width, terrain_texture='white_cube', rendering_distance=10, size_render=5, amp=5, polig_size=1):
        super().__init__()
        self.player = player
        self.terrain_width = terrain_width if terrain_width % 2 == 0 else terrain_width+1
        self.noise = PerlinNoise(octaves=3,seed=1)
        self.model = Mesh(vertices=[], uvs=[])
        self.rendering_distance = rendering_distance
        self.size_render = size_render
        self.polig_size = polig_size
        self.amp = amp
        for z, x in itertools.product(range(self.terrain_width), range(self.terrain_width)):
            self.render_map(x,z)
        self.model = Mesh(vertices=self.model.vertices, uvs=self.model.vertices)
        self.texture = terrain_texture
        self.texture_scale=self.polig_size
        self.middle = Vec3(self.model.vertices[len(self.model.vertices) // 2-self.terrain_width*3]) + Vec3(-1,0,0)
        self.rendering = False
        
    def update(self):
        if self.rendering == 'end':
            self.model.uvs = self.model.vertices
            self.model.generate()
            self.rendering = False
        if self.player.z > self.middle[2] + self.terrain_width/2 -self.rendering_distance and self.rendering == False:
            self.rendering = 'z+'
            _thread.start_new_thread(self.move_map, ())
        if self.player.z < self.middle[2] - self.terrain_width/2 +self.rendering_distance and self.rendering == False:
            self.rendering = 'z-'
            _thread.start_new_thread(self.move_map, ())
        if self.player.x > self.middle[0] + self.terrain_width/2 -self.rendering_distance and self.rendering == False:
            self.rendering = 'x+'
            _thread.start_new_thread(self.move_map, ())
        if self.player.x < self.middle[0]- self.terrain_width/2 +self.rendering_distance and self.rendering == False:
            self.rendering = 'x-'
            _thread.start_new_thread(self.move_map, ())
        
    def move_map(self):
        if self.rendering == 'z+':
            for _ in range(self.size_render):
                ground_pos = self.model.vertices[-(self.terrain_width*6-1)]
                for c in range(self.terrain_width):
                    self.render_map(c+ground_pos[0]+.5+self.terrain_width/2, ground_pos[2]+.5+self.terrain_width/2, len(self.model.vertices))
            self.model.vertices = self.model.vertices[(self.terrain_width*6)*self.size_render:]
        if self.rendering == 'z-':
            for _ in range(self.size_render):
                ground_pos = self.model.vertices[2]
                for c in range(self.terrain_width):
                    self.render_map(-c+ground_pos[0]-.5+self.terrain_width/2+self.terrain_width, ground_pos[2]-.5+self.terrain_width/2, 0)
            self.model.vertices = self.model.vertices[:-(self.terrain_width*6)*self.size_render]
        if self.rendering == 'x+':
            for _ in range(self.size_render):
                ground_pos = self.model.vertices[-2]
                for c in range(self.terrain_width):
                    self.render_map(ground_pos[0]+.5+self.terrain_width/2,c+ground_pos[2]+.5-self.terrain_width/2,(self.terrain_width*6)*c+(self.terrain_width*6))
                    for _ in range(6):
                        self.model.vertices.pop(c*(self.terrain_width*6))
        if self.rendering == 'x-':
            for _ in range(self.size_render):
                ground_pos = self.model.vertices[2]
                for c in range(self.terrain_width):
                    self.render_map(ground_pos[0]-.5+self.terrain_width/2,c+ground_pos[2]+.5+self.terrain_width/2,c*(self.terrain_width*6))
                    for _ in range(6):
                        self.model.vertices.pop((self.terrain_width*6)*c+(self.terrain_width*6))
        self.middle = Vec3(self.model.vertices[len(self.model.vertices) // 2-self.terrain_width*3]) + Vec3(-1,0,0)
        self.rendering = 'end'
    
    def render_map(self,x,z,index= None):
        y = self.noise([x/self.terrain_width, z/self.terrain_width])*self.amp
        if index is None:
            self.model.vertices.append((x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.append((x-self.terrain_width/2 -0.5, y+ (self.noise([(x)/self.terrain_width, (z+1)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.append((x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
            self.model.vertices.append((x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 -0.5))
            self.model.vertices.append((x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.append((x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
        else:
            self.model.vertices.insert(index,(x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 -0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 -0.5, y, z-self.terrain_width/2 -0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 -0.5, y+ (self.noise([(x)/self.terrain_width, (z+1)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 +0.5))
            self.model.vertices.insert(index,(x-self.terrain_width/2 +0.5, y+ (self.noise([(x+1)/self.terrain_width, (z+1)/self.terrain_width])*self.amp -y), z-self.terrain_width/2 +0.5))
            sleep(0.001*time.dt) # slowing down the map rendering process so it doesn't affect the rest of the game
    def return_terrain_y(self,x,z):
        return self.noise([(x+self.terrain_width/2+0.5)/self.terrain_width, (z+self.terrain_width/2+.5)/self.terrain_width])*self.amp
    

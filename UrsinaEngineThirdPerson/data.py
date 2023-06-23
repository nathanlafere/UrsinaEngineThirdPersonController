from ursina import *

ground = None
player_model = "assets/archer.gltf"
last_move_button = (0,0) # [0]key [1]time
last_attack_button = (0,0,0) # [0]key [1]time [2]combo len
animation_jump = {'rise','falling','land'}
animation_attack = {
    'bow-w': 'attack_forward',
    'bow-s': 'attack_back',
    'bow-d': 'attack_right',
    'bow-a': 'attack_left',
    'sword-w': 'attack_forward',
    'sword-s': 'attack_back',
    'sword-d': 'attack_right',
    'sword-a': 'attack_left'
}

class Character(Entity):
    def __init__(self):
        super().__init__()
        self.str = 6
        self.vit = 1
        self.agi = 1
        self.luk = 5
        self.speed = 4
        self.health = [60,60]
        self.mana = [40,40]
        self.experience = [0,120]
        self.invulnerable = False
        self.height = 2
        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.air_time = 0
        self.fall_after = .35
        self.jumping = False
        
        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            if ray.hit:
                self.y = ray.world_point.y

    def gravity_update(self):
        if not self.gravity:
            return
        left_ray = raycast(self.world_position+(0,self.height,0)+self.right*0.2+self.back*0.3, self.down, ignore=(self,))
        right_ray = raycast(self.world_position+(0,self.height,0)+self.left*0.2+self.forward*0.3, self.down, ignore=(self,))
        middle_ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
        terrain_y = ground.return_terrain_y(self.x, self.z)
        if middle_ray.distance <= self.height+.1 or self.y - terrain_y <= .1:
            if not self.grounded:
                self.land()
            self.grounded = True
            # make sure it's not a wall and that the point is not too far up
            if (# walk up slope
                middle_ray.world_normal != None  
                and middle_ray.world_normal.y > .7 
                and middle_ray.world_point.y - self.world_y < .5 
            ):
                self.y = middle_ray.world_point[1]
            elif terrain_y >= self.y and self.y - terrain_y < .5 or terrain_y <= self.y and self.y - terrain_y < .5:
                self.y = terrain_y
            return
        elif left_ray.distance <= self.height+.1 and right_ray.distance <= self.height+.1 or self.y - terrain_y <= .1:
            return
        else:
            self.grounded = False
        # if not on ground and not on way up in jump, fall
        self.y -= min(self.air_time, middle_ray.distance-.05, self.y - terrain_y-.05) * time.dt * 100
        self.air_time += time.dt * .25 * self.gravity
        terrain_y = ground.return_terrain_y(self.x,self.z)
        if self.position[1] <= terrain_y-10:
            self.y = terrain_y+2
        
    # jump functions
    def jump(self):
        if not self.grounded:
            return
        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fall_after)
        
    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False
        
    def land(self):
        self.air_time = 0
        self.grounded = True
            
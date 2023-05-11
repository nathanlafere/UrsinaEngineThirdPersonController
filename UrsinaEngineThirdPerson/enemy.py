from ursina import *
import random
import data

class Enemy(Entity):
    def __init__(self,health,**kwargs):
        super().__init__()
        self.position = (0,data.ground.y,0)
        self.speed = 4
        self.aggressive_speed = 6
        self.health = health
        self.aggressive = False
        self.stuck = False
        self.combat = False
        self.height = self.scale_y
        self.collider = "box"
        self.collider = SphereCollider(self, center=Vec3(0,0,0), radius=.2)
        self.resting = True
        self.attack_range = 0.5
        self.target = None
        self.rest_time, self.walk_time = 8, 5
        self.time_rested, self.walked_time  = 0, 0
        for key, value in kwargs.items():
            setattr(self, key ,value)

    def update(self):
        if not self.stuck:
            if self.combat:
                self.choice_walk_direction()
                self.walk(self.attack_range)
            else:
                if self.aggressive:
                    self.find_target()
                if self.resting:
                    if self.time_rested <=0:
                        self.resting = not self.resting
                        self.choice_walk_direction()
                    else:
                        self.time_rested -= 1*time.dt
                if self.walked_time <=0:
                    if self.time_rested <=0:
                        self.resting = not self.resting
                        self.time_rested = self.rest_time
                        self.walked_time = self.walk_time
                elif not self.resting:
                    self.walked_time -= 1*time.dt
                    self.walk()
        elif not self.combat:
            self.find_target()
        if self.health <= 0:
            destroy(self)
        
    def choice_walk_direction(self):
        if self.combat:
            self.look_at_2d(self.target,'y')
            self.direction = (Vec3(getattr(self.target, "position"))-self.position).normalized()
            self.direction[1] = 0
            hitbox=boxcast(origin=self.position+Vec3(0,0.4,0),direction=self.forward,distance=1.8,thickness=(1,2),ignore=[self,data.ground])
        else:
            possible_directions = [(1,0,1),(1,0,-1),(-1,0,1),(-1,0,-1),(0,0,-1),(0,0,+1),(-1,0,0),(1,0,0)]
            self.direction = Vec3(random.choice(possible_directions)).normalized()
            self.look_at_2d(self.position+self.direction,'y')
        
    def find_target(self):
        print(' ')
    
    def walk(self,range=0):
        feet_ray = raycast(self.position+Vec3(0,0.2,0), self.direction, ignore=(self,), distance=.5+range)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5+range)
        if not feet_ray.hit and not head_ray.hit:
            move_amount = self.direction * time.dt * self.aggressive_speed if self.combat else self.direction * time.dt * self.speed
            if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, ignore=(self,)).hit:
                move_amount[0] = min(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, ignore=(self,)).hit:
                move_amount[0] = max(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, ignore=(self,)).hit:
                move_amount[2] = min(move_amount[2], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, ignore=(self,)).hit:
                move_amount[2] = max(move_amount[2], 0)
            self.position += move_amount

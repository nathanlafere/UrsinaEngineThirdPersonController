from ursina import *
import random
import data
from panda3d import *
from direct.actor.Actor import Actor

class Enemy(Entity):
    def __init__(self,health,**kwargs):
        super().__init__()
        self.position = (0,data.ground.y,0)
        self.height = self.scale_y
        self.collider = "box"
        self.collider = SphereCollider(self, center=Vec3(0,0,0), radius=.2)
        self.target = None
        self.rest_time, self.walk_time = 8, 5
        self.time_rested, self.walked_time  = 0, 0
        
        #attributes
        self.health = health
        self.defense = 1
        self.attack = 3
        self.speed = 4
        self.aggressive_speed = 6
        self.aggressive = False
        self.attack_speed = 1.3
        self.attack_range = 0.5
        
        #state
        self.invulnerable = False
        self.stuck = False
        self.combat = False
        self.resting = True
        
        for key, value in kwargs.items():
            setattr(self, key ,value)
        self.actor = Actor(self.actor)
        self.actor.reparentTo(self)
            

    def update(self):
        if self.actor.get_current_anim() == "enemy_action_attack" and self.actor.getCurrentFrame("enemy_action_attack") == 37:
                hitbox=boxcast(origin=self.position+Vec3(0,0.4,0),direction=self.forward,distance=.5+self.attack_range,thickness=(1,2),ignore=[self,data.ground])
                if hitbox.hit:
                    self.apply_damage(hitbox.entity,self.attack)
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
        else:
            possible_directions = [(1,0,1),(1,0,-1),(-1,0,1),(-1,0,-1),(0,0,-1),(0,0,+1),(-1,0,0),(1,0,0)]
            self.direction = Vec3(random.choice(possible_directions)).normalized()
            self.look_at_2d(self.position+self.direction,'y')
        
    def find_target(self):
        print(' ')
        
    
    def walk(self,range=0):
        feet_ray = raycast(self.position+Vec3(0,0.2,0), self.direction, ignore=(self,), distance=.5+range)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5+range)
        if not feet_ray.hit and not head_ray.hit and self.actor.get_current_anim() != "enemy_action_attack":
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
        if feet_ray or head_ray:
            self.actor.play("enemy_action_attack")

    def apply_damage(self,entity,damage):
        if hasattr(entity,"health") and not getattr(entity,"invulnerable"):
            entity.health -= damage - getattr(entity, "defense")
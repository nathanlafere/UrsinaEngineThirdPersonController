from ursina import *
import random
import data
from panda3d import *
from direct.actor.Actor import Actor

class Enemy(Entity):
    def __init__(self,health,actor_model,**kwargs):
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
        self.attack_speed = 1.1
        self.attack_range = 1.3
        
        #state
        self.invulnerable = False
        self.stuck = False
        self.combat = False
        self.resting = True
        self.already_reached = False
        
        for key, value in kwargs.items():
            setattr(self, key ,value)
        
        self.actor_model = actor_model
        self.actor = Actor(self.actor_model)
        self.actor.reparentTo(self)

    def update(self):
        
        
        print(self.actor.getAnimNames(),self.actor.getCurrentFrame())
                
                
        if self.actor.get_current_anim() == "Attack_Action" and self.actor.getCurrentFrame("Attack_Action") >= 28 and not self.already_reached:
                hitbox=boxcast(origin=self.position+Vec3(0,0.4,0),direction=self.forward,distance=.5+self.attack_range,thickness=(1,2),ignore=[self,data.ground],debug=True)
                if hitbox.hit:
                    self.already_reached = True
                    self.apply_damage(hitbox.entity,self.attack)
        if not self.stuck:
            if self.combat:
                self.choice_walk_direction()
                self.raycast_walk(self.attack_range)
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
                        if self.actor.getCurrentAnim() == "enemy_action_walk":
                            self.actor.stop("enemy_action_walk")
                        self.resting = not self.resting
                        self.time_rested = self.rest_time
                        self.walked_time = self.walk_time
                elif not self.resting:
                    self.walked_time -= 1*time.dt
                    self.raycast_walk()
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
        
    
    def raycast_walk(self,range=0):
        feet_ray = raycast(self.position+Vec3(0,0.2,0), self.direction, ignore=(self,), distance=.5+range)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5+range)
        if feet_ray and self.actor.get_current_anim() != 'Attack_Action' or head_ray and self.actor.get_current_anim() != 'Attack_Action':
            self.actor.play('Attack_Action')
            self.already_reached = False
        if not feet_ray.hit and not head_ray.hit and self.actor.get_current_anim() != "Attack_Action":
            self.walk()

    def walk(self):
        if self.actor.get_current_anim() != 'enemy_action_walk':
            self.actor.loop('enemy_action_walk')
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

    def apply_damage(self,entity,damage):
        if (
            hasattr(entity, "health")
            and not getattr(entity, "invulnerable")
            and damage > getattr(entity, "defense")
        ):
            entity.health -= damage - getattr(entity, "defense")
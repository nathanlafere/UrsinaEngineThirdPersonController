from collections import defaultdict
from ursina import *
import random
import data
from panda3d import *
from direct.actor.Actor import Actor

    
class Enemy(Entity,data.Character):
    __refs__ = defaultdict(list)
    def __init__(self,actor_model,position,**kwargs):
        super().__init__()
        data.Character.__init__(self)
        self.__refs__['enemys'].append(self)
        self.position = position
        self.y = data.ground.y
        self.height = self.scale_y
        self.target = None
        self.rest_time, self.walk_time = 8, 5
        self.time_rested, self.walked_time  = 0, 0
        
        #attributes
        self.defense = 1
        self.attack = 3
        self.aggressive = False
        self.attack_ranges = [.3,1.7]  # [0]range to attack  [1]attack range
        self.gravity = 1
        
        #state
        self.stuck = False
        self.in_combat = False
        self.resting = True
        self.already_reached = False
        self.grounded = False
        self.air_time = 0
        
        for key, value in kwargs.items():
            setattr(self, key ,value)
        
        self.actor_model = actor_model
        self.actor = Actor(self.actor_model)
        self.actor.reparentTo(self)
        self.collider = SphereCollider(self,center=(0,0,0),radius=0.2)
        
        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            if ray.hit:
                self.y = ray.world_point.y

    def update(self):
        if self.actor.get_current_anim() == "enemy_action_attack" and self.actor.getCurrentFrame("enemy_action_attack") >= 28 and not self.already_reached:
            atq_hitbox = boxcast(origin=self.position+Vec3(0,0.4,0), direction=self.forward, distance=sum(self.attack_ranges), thickness=(1,1.5),ignore=list(Enemy.__refs__['enemys'])+[data.ground,])
            if atq_hitbox.hit:
                self.already_reached = True
                self.apply_damage(atq_hitbox.entity,self.attack)
        
        if not self.stuck:
            self.behavior_control()
        
        elif not self.in_combat:
            self.find_target()
        if self.health <= 0:
            destroy(self)
        
        if self.gravity:
            self.apply_gravity()


    def choice_walk_direction(self):
        if self.in_combat:
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
        feet_ray = raycast(self.position+Vec3(0,0.2,0), self.direction, ignore=list(Enemy.__refs__['enemys']), distance=.2+range)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=list(Enemy.__refs__['enemys']), distance=.2+range)
        if feet_ray.hit or head_ray.hit:
            if self.in_combat and any((hasattr(feet_ray.entity,'health'), hasattr(head_ray.entity,'health'))):
                if self.actor.get_current_anim() != "enemy_action_attack":
                    self.actor.play("enemy_action_attack")
                    self.already_reached = False
            else:
                self.choice_walk_direction()
        elif self.actor.get_current_anim() != "enemy_action_attack" and self.grounded:
            self.walk()

    def walk(self):
        if self.actor.get_current_anim() != "enemy_action_walk":
            self.actor.loop("enemy_action_walk")
        move_amount = self.direction * time.dt * self.speed*1.6 if self.in_combat else self.direction * time.dt * self.speed
        self.position += move_amount
    
    def land(self):
        self.air_time = 0
        self.grounded = True

    def apply_gravity(self):
        ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=list(Enemy.__refs__['enemys']))  ###
        if ray.distance <= self.height+.1:
            if not self.grounded:
                self.land()
            self.grounded = True
            # make sure it's not a wall and that the point is not too far up
            if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5 and not hasattr(ray.entity,'health'): # walk up slope
                self.y = ray.world_point[1]
            return
        else:
            self.grounded = False
            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity

            if self.position[1] <= -30:
                self.position = (1,5,1)

    def apply_damage(self,entity,damage):
        if (
            hasattr(entity, "health")
            and not getattr(entity, "invulnerable")
            and damage > getattr(entity, "defense")
        ):
            entity.health -= damage - getattr(entity, "defense")
            
    def behavior_control(self):
        if self.in_combat and self.actor.get_current_anim() != 'enemy_action_attack':
            self.choice_walk_direction()
            self.raycast_walk(self.attack_ranges[0])
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

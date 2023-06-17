from ursina import *
import data
from panda3d import *
from direct.actor.Actor import Actor

class Portal(Entity):
    def __init__(self,exit_position,position,**kwargs):
        super().__init__(**kwargs)
        if len(position) == 2:
            self.position = (position[0],data.ground.return_terrain_y(position[0],position[1]),position[1])
        if len(exit_position) == 2:
            self.exit_position = (exit_position[0],data.ground.return_terrain_y(exit_position[0],exit_position[1]),exit_position[1])
        self.conected_portal = Entity(position=self.exit_position, **kwargs)
        self.actor_1 = Actor("assets/Portal")
        self.actor_1.reparentTo(self)
        self.actor_2 = Actor("assets/Portal")
        self.actor_2.reparentTo(self.conected_portal)
        for key, value in kwargs.items():
            setattr(self, key ,value)
            
    def update(self):
        hitbox_1 = boxcast(self.position+(0,2,0), direction=self.forward, distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self))
        hitbox_2 = boxcast(Vec3(self.exit_position)+(0,2,0), direction=self.forward, distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self))
        if hitbox_1.hit:
            self.teleport(hitbox_1.entity,Vec3(self.exit_position)+self.forward*3)
        if hitbox_2.hit:
            if hasattr(hitbox_2.entity,"health"):
                self.teleport(hitbox_2.entity,Vec3(self.position)+self.forward*3)
                
    def teleport(self,hit_entity,position):
        if hasattr(hit_entity,"health"):
            if hit_entity.type == "Enemy":
                hit_entity.direction = self.forward
            setattr(hit_entity,"position",position)
            setattr(hit_entity,"rotation_y",self.rotation_y)

class Bridge():
    def __init__(self, position, railings='cube', ground='cube', texture='brick',collider='box', distance=5, direct='x', width=5):
        self.position = position
        railings_direct = -1 if direct=='z' else 1
        ground_direct = -1 if direct=='z' else 1
        if railings == 'cube':
            Entity(model=railings,scale=(distance-1,0.5,1)[::railings_direct],texture=texture, texture_scale=(distance-1,1),collider=collider, position=Vec3(self.position)+Vec3((0,distance/2+1,width/2)[::railings_direct]))
            Entity(model=railings,scale=(distance-1,0.5,1)[::railings_direct],texture=texture, texture_scale=(distance-1,1),collider=collider, position=Vec3(self.position)+Vec3((0,distance/2+1,-width/2)[::railings_direct]))
            for c in range(distance+2):
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::railings_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((distance/2+c,distance/2-c*0.5+.5,width/2)[::railings_direct]))
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::railings_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((-distance/2-c,distance/2-c*0.5+.5,width/2)[::railings_direct]))
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::railings_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((distance/2+c,distance/2-c*0.5+.5,-width/2)[::railings_direct]))
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::railings_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((-distance/2-c,distance/2-c*0.5+.5,-width/2)[::railings_direct]))
        else:
            r_model_direct = 90 if direct=='z' else 0
            Entity(model=railings,collider=collider, position=Vec3(self.position)+Vec3((0,0,width/2)[::railings_direct]), rotation_y=r_model_direct)
            Entity(model=railings,collider=collider, position=Vec3(self.position)+Vec3((0,0,-width/2)[::railings_direct]), rotation_y=r_model_direct)
        if ground == 'cube':
            for c in range(int(distance*2.7)):
                Entity(model=ground, scale=(0.55,0.25,width)[::ground_direct],texture=texture, collider=collider, position=Vec3(self.position)+Vec3((c*0.51+distance/2,distance/2-c*0.2,0)[::ground_direct]))
                Entity(model=ground, scale=(0.55,0.25,width)[::ground_direct],texture=texture, collider=collider, position=Vec3(self.position)+Vec3((-c*0.51-distance/2,distance/2-c*0.2,0)[::ground_direct]))
            Entity(model=ground, scale=(distance,0.25,width)[::ground_direct],texture=texture, texture_scale=(distance,2), collider=collider, position=Vec3(self.position)+Vec3((0,distance/2+0.2,0)[::ground_direct]))
        else:
            ground_model_direct = 90 if direct=='z' else 0
            Entity(model=ground,collider=collider,position=Vec3(self.position), rotation_y = ground_model_direct)

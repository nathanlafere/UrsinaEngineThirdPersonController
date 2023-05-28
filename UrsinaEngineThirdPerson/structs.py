from ursina import *
import data
from panda3d import *
from direct.actor.Actor import Actor

class Portal(Entity):
    def __init__(self,exit_position,position,**kwargs):
        super().__init__(**kwargs)
        self.exit_position = exit_position
        self.position = position
        conected_portal = Entity(position=Vec3(exit_position), **kwargs)
        self.actor_1 = Actor("assets/Portal.egg")
        self.actor_1.reparentTo(self)
        self.actor_2 = Actor("assets/Portal.egg")
        self.actor_2.reparentTo(conected_portal)
        
        for key, value in kwargs.items():
            setattr(self, key ,value)
            
    def update(self):
        hitbox_2 = boxcast(Vec3(self.exit_position)+(0,2,0), direction=self.forward, distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self))
        hitbox_1 = boxcast(self.position+(0,2,0), direction=self.forward, distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self))
        if hitbox_1.hit:
            if hasattr(hitbox_1.entity,"health"):
                setattr(hitbox_1.entity,"position",Vec3(self.exit_position)+self.forward*3)
                if hasattr(hitbox_1.entity,"cursor"):
                    setattr(hitbox_1.entity,"rotation_y",self.rotation_y)
        if hitbox_2.hit:
            if hasattr(hitbox_2.entity,"health"):
                setattr(hitbox_2.entity,"position",Vec3(self.position)+self.forward*3)
                if hasattr(hitbox_2.entity,"cursor"):
                    setattr(hitbox_2.entity,"rotation_y",self.rotation_y)

class Bridge():
    def __init__(self, position, railings='cube', ground='cube', texture='brick',collider='box', distance=5, direct='x', width=5):
        self.position = position
        r_direct = -1 if direct=='z' else 1
        g_direct = -1 if direct=='z' else 1
        if railings == 'cube':
            Entity(model=railings,scale=(distance-1,0.5,1)[::r_direct],texture=texture, texture_scale=(distance-1,1),collider=collider, position=Vec3(self.position)+Vec3((0,distance/2+1,width/2)[::r_direct]))
            Entity(model=railings,scale=(distance-1,0.5,1)[::r_direct],texture=texture, texture_scale=(distance-1,1),collider=collider, position=Vec3(self.position)+Vec3((0,distance/2+1,-width/2)[::r_direct]))
            for c in range(distance+2):
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::r_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((distance/2+c,distance/2-c*0.5+.5,width/2)[::r_direct]))
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::r_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((-distance/2-c,distance/2-c*0.5+.5,width/2)[::r_direct]))
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::r_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((distance/2+c,distance/2-c*0.5+.5,-width/2)[::r_direct]))
                Entity(model=railings,scale=(1.53+c*0.5,0.5,1)[::r_direct],texture=texture, texture_scale=(1.5+c,1),collider=collider, position=Vec3(self.position)+Vec3((-distance/2-c,distance/2-c*0.5+.5,-width/2)[::r_direct]))
        else:
            r_model_direct = 90 if direct=='z' else 0
            Entity(model=railings,collider=collider, position=Vec3(self.position)+Vec3((0,0,width/2)[::r_direct]), rotation_y=r_model_direct)
            Entity(model=railings,collider=collider, position=Vec3(self.position)+Vec3((0,0,-width/2)[::r_direct]), rotation_y=r_model_direct)
        if ground == 'cube':
            for c in range(int(distance*2.7)):
                Entity(model=ground, scale=(0.55,0.25,width)[::g_direct],texture=texture, collider=collider, position=Vec3(self.position)+Vec3((c*0.51+distance/2,distance/2-c*0.2,0)[::g_direct]))
                Entity(model=ground, scale=(0.55,0.25,width)[::g_direct],texture=texture, collider=collider, position=Vec3(self.position)+Vec3((-c*0.51-distance/2,distance/2-c*0.2,0)[::g_direct]))
            Entity(model=ground, scale=(distance,0.25,width)[::g_direct],texture=texture, texture_scale=(distance,2), collider=collider, position=Vec3(self.position)+Vec3((0,distance/2+0.2,0)[::g_direct]))
        else:
            g_model_direct = 90 if direct=='z' else 0
            Entity(model=ground,collider=collider,position=Vec3(self.position), rotation_y = g_model_direct)
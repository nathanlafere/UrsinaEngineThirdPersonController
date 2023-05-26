from ursina import *
import data
from panda3d import *
from direct.actor.Actor import Actor

class Portal(Entity):
    def __init__(self,exit_position,position,**kwargs):
        super().__init__(**kwargs)
        self.exit_position = exit_position
        self.position = position
        conected_portal = Entity(position=Vec3(exit_position))
        self.actor_1 = Actor("assets/Portal.egg")
        self.actor_1.reparentTo(self)
        self.actor_2 = Actor("assets/Portal.egg")
        self.actor_2.reparentTo(conected_portal)
        
        for key, value in kwargs.items():
            setattr(self, key ,value)
            
    def update(self):
        hitbox_2 = boxcast(Vec3(self.exit_position)+(0,2,0), direction=(0,0,1), distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self))
        hitbox_1 = boxcast(self.position+(0,2,0), direction=(0,0,1), distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self))
        if hitbox_1.hit:
            if hasattr(hitbox_1.entity,"health"):
                setattr(hitbox_1.entity,"position",Vec3(self.exit_position)+(0,0,3))
                if hasattr(hitbox_1.entity,"cursor"):
                    setattr(hitbox_1.entity,"rotation_y",self.rotation_y)
        if hitbox_2.hit:
            if hasattr(hitbox_2.entity,"health"):
                setattr(hitbox_2.entity,"position",Vec3(self.position)+(0,0,3))
                if hasattr(hitbox_2.entity,"cursor"):
                    setattr(hitbox_2.entity,"rotation_y",self.rotation_y)

class Bridge():
    def __init__(self, position, railings='cube', ground='plane', **kwargs):
        self.position = position
        
        if railings == 'cube':
            for c in range(10):
                self.railings = [
                    Entity(model=railings,collider='box', position=Vec3(self.position)+Vec3(c*1.01,5-c*0.51,2.5)),
                    Entity(model=railings,collider='box', position=Vec3(self.position)+Vec3(-c*1.01,5-c*0.51,2.5)),
                    Entity(model=railings,collider='box', position=Vec3(self.position)+Vec3(c*1.01,5-c*0.51,-2.5)),
                    Entity(model=railings,collider='box', position=Vec3(self.position)+Vec3(-c*1.01,5-c*0.51,-2.5))
                ]
        if ground == 'plane':
            self.ground = Entity(model=ground, position=self.position)
        

from ursina import *
import data
from panda3d import *
from direct.actor.Actor import Actor

class Portal(Entity):
    def __init__(self,exit_position,**kwargs):
        super().__init__()
        self.exit_position = exit_position
        self.model = "cube"
        self.scale = (4,4,0.3)
        conected_portal = Entity(model="cube",scale=(4,4,0.3),position=Vec3(exit_position)+(0,2,0))
        
        for key, value in kwargs.items():
            setattr(self, key ,value)
            
            
    
    def update(self):
        print(self.position+(0,0,3), Vec3(self.exit_position)+(0,0,3))
        hitbox_2 = boxcast(Vec3(self.exit_position)+(0,2,0), direction=(0,0,1), distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self), debug=True)
        hitbox_1 = boxcast(self.position, direction=(0,0,1), distance=0.3, thickness=(4,4), traverse_target=scene, ignore=(data.ground,self), debug=True)
        if hitbox_1.hit:
            if hasattr(hitbox_1.entity,"health"):
                setattr(hitbox_1.entity,"position",Vec3(self.exit_position)+(0,0,3))
                if hasattr(hitbox_1.entity,"cursor"):
                    setattr(hitbox_1.entity,"rotation_y",self.rotation_y)
        if hitbox_2.hit:
            if hasattr(hitbox_2.entity,"health"):
                setattr(hitbox_2.entity,"position",Vec3(self.position)+(0,-2,3))
                if hasattr(hitbox_2.entity,"cursor"):
                    setattr(hitbox_2.entity,"rotation_y",self.rotation_y)
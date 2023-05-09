from ursina import *
import data
from panda3d import *
from direct.actor.Actor import Actor

class ThirdPersonController(Entity):
    def __init__(self, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        self.speed = 6
        self.running_speed = 9
        self.height = 2
        self.camera_pivot = Entity(parent=self, y=self.height)

        camera.parent = self.camera_pivot
        camera.position = (0,10,-15)
        camera.rotation = (25,0,0)
        
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.running = False
        self.damage = 3
        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35
        self.jumping = False
        self.air_time = 0

        for key, value in kwargs.items():
            setattr(self, key ,value)

        self.actor = Actor(data.player_model)
        self.actor.setH(180)
        self.actor.reparentTo(self)

        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            if ray.hit:
                self.y = ray.world_point.y


    def update(self):        
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -20, 50)
        camera.position = clamp(camera.position,(0,1,-6),(0,13,-18))
        camera.rotation_x = clamp(camera.rotation_x, 7,31)
        # release cam
        if held_keys['left alt']:
            self.camera_pivot.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
        else:
            self.camera_pivot.rotation_y = 0
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()
        if self.check_raycast():
            self.walk()


        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

            if ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity

            if self.position[1] <= -30:
                self.position = (1,5,1)


    def input(self, key):
        if key == 'scroll down':
            camera.position += (0,-1,1)
            camera.rotation_x -= 2
        elif key == 'scroll up':
            camera.position += (0,1,-1)
            camera.rotation_x += 2
        self.rotateModel()
        
        # running system and animation
        self.running = bool(
            held_keys['left shift']
            and any([held_keys['w'], held_keys['a'], held_keys['d']])
            and not held_keys['s']
            or self.running
            and any([held_keys['w'], held_keys['a'], held_keys['d']])
            and not held_keys['s']
        )
        if self.running:
            if self.actor.getCurrentAnim() != data.player_action_running:
                self.actor.loop(data.player_action_running)
            if held_keys['a']*held_keys['d'] and not held_keys['w']:
                self.actor.stop()
        else:
            self.actor.stop()
        
        
        if key == 'space':
            self.jump()
        if key == 'left mouse down' and self.grounded:
            hitbox=boxcast(origin=self.position+Vec3(0,1.1,0),direction=self.forward,distance=2.8,thickness=(2,3),ignore=[self])
            if hitbox.hit:
                self.apply_damage(hitbox.entity,self.damage*0.7)
        if key in ['w','a','s','d']:
            if key == data.last_move_button[0] and time.process_time() < data.last_move_button[1]+.4:
                self.animate('position', self.position+Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()*time.dt*950, duration= 0.2, curve=curve.linear)
                self.running = True
                data.last_move_button = (0,0,time.process_time()+4)
            elif data.last_move_button[2] == 0 or data.last_move_button[2] < time.process_time():
                data.last_move_button = (key,time.process_time(),0)


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

    #applies damage and some status changes after hitting something
    def apply_damage(self,entity,damage):
        if hasattr(entity,"health"):
            if not getattr(entity,"combat"):
                entity.combat = True
            if getattr(entity, "target") is None:
                entity.target = self
            entity.health -= damage

    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True
        
    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False
    
    #confirm that it won't hit anything
    def check_raycast(self,range=0):
        feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, ignore=(self,), distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.4,0), self.direction, ignore=(self,), distance=.5, debug=False)
        chest_ray = raycast(self.position+Vec3(0,self.height/2,0), self.direction, ignore=(self,), distance=.5, debug=False)
        if not feet_ray.hit and not head_ray.hit and not chest_ray:
            return True
    
    def walk(self):
        move_amount = self.direction * time.dt * self.running_speed if self.running else self.direction * time.dt * self.speed 
        if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, ignore=(self,)).hit:
            move_amount[0] = min(move_amount[0], 0)
        if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, ignore=(self,)).hit:
            move_amount[0] = max(move_amount[0], 0)
        if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, ignore=(self,)).hit:
            move_amount[2] = min(move_amount[2], 0)
        if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, ignore=(self,)).hit:
            move_amount[2] = max(move_amount[2], 0)
        self.position += move_amount
            
    #Rotate de character model
    def rotateModel(self):
        if held_keys['w'] or held_keys['s']:
            self.actor.setH(180)
        if held_keys['a'] and not held_keys['a']*held_keys['w']*held_keys['d']:
            self.actor.setH(270-held_keys['w']*45-held_keys['s']*135)
        if held_keys['d'] and not held_keys['a']*held_keys['w']*held_keys['d']:
            self.actor.setH(90+held_keys['w']*45+held_keys['s']*135)
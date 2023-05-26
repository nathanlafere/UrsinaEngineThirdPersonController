from ursina import *
import data
from panda3d import *
from direct.actor.Actor import Actor

class ThirdPersonController(Entity,data.Character):
    def __init__(self, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        data.Character.__init__(self)
        self.height = 2
        self.camera_pivot = Entity(parent=self, y=self.height)

        camera.parent = self.camera_pivot
        camera.position = (0,10,-15)
        camera.rotation = (25,0,0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)
        

        #attributes
        self.attack = 5
        self.defense = 1
        self.gravity = 1
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35
        self.weapon = "bow"
        
        #state
        self.in_dash = False
        self.jumping = False
        self.grounded = False
        self.running = False
        self.cooldowns = [0,0,0]  #[0] basic attack, [1] dash, [2] spell attack
        self.air_time = 0
        
        for key, value in kwargs.items():
            setattr(self, key ,value)

        self.actor = Actor(data.player_model)
        self.actor.setH(180)
        self.actor.reparentTo(self)
        self.collider = BoxCollider(self,center=Vec3(0,0.85,0),size=(1,1.75,1))
        
        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            if ray.hit:
                self.y = ray.world_point.y


    def update(self):
        if held_keys['a']+held_keys['d']+held_keys['w']+held_keys['s']:
            self.rotateModel()
            self.move_animation()
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]

        camera.position = clamp(camera.position,(0,1,-6),(0,13,-18))
        camera.rotation_x = clamp(camera.rotation_x, 7,31)
        # release cam
        if held_keys['left alt']:
            self.camera_pivot.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -28, 80)
        else:
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -20, 50)
            self.camera_pivot.rotation_y = 0
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()
        if mouse.moving and self.direction == 0 and self.actor.getH != 180:
            self.actor.setH(180)
        if self.check_raycast():
            self.walk()


        if self.gravity:
            left_ray = raycast(self.world_position+(0,self.height,0)+self.right*0.2+self.back*0.3, self.down, ignore=(self,))
            right_ray = raycast(self.world_position+(0,self.height,0)+self.left*0.2+self.forward*0.3, self.down, ignore=(self,))
            middle_ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
            if middle_ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if middle_ray.world_normal != None and middle_ray.world_normal.y > .7 and middle_ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = middle_ray.world_point[1]
                return
            elif left_ray.distance <= self.height+.1 and right_ray.distance <= self.height+.1:
                return
            else:
                self.grounded = False
            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, middle_ray.distance-.05) * time.dt * 100
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
        if key == 'space':
            self.jump()
        if key == 'left mouse down':
            if self.in_dash:
                self.dash_attack()
            elif self.cooldowns[0] < time.process_time():
                if self.running:
                    self.speed -= 1.5
                    invoke(setattr,self,'speed',self.speed+1.5,delay=0.2)
                self.cooldowns[0] = time.process_time() + 80*time.dt
                self.combo_attack()
        self.running = bool(
            held_keys['left shift']
            and held_keys['w']+ held_keys['a']+ held_keys['d']
            and not held_keys['s']
            or self.running
            and held_keys['w']+ held_keys['a']+ held_keys['d']
            and not held_keys['s']
        )
        if key in ['w','a','s','d']:
            # Dash implements
            if key == data.last_move_button[0] and time.process_time() < data.last_move_button[1]+.3 and time.process_time() > self.cooldowns[1]:
                self.dash()
            else:
                data.last_move_button = (key,time.process_time())
        if held_keys['a']*held_keys['d'] and not any([held_keys['w'],held_keys['s']]) or not any([held_keys['w'],held_keys['a'],held_keys['d'],held_keys['s']]) :
            if self.actor.getCurrentAnim() not in ['attack_back', 'attack', 'attack_left', 'attack_forward', 'attack_right', 'idle']:
                self.actor.loop('idle')

    def combo_attack(self):
        self.actor.play('attack',fromFrame=self.actor.getCurrentFrame())
        if time.process_time() < data.last_attack_button[1]+1+self.cooldowns[0] and data.last_attack_button[2] < 2 or data.last_attack_button[1] == 0:
            data.last_attack_button = ['left mouse down',time.process_time(),data.last_attack_button[2]+1]
        else:
            data.last_attack_button = ['left mouse down',time.process_time(),0]
        if data.last_attack_button[2] == 2:
            self.animate('position', self.position+Vec3(self.back).normalized()*2, duration= 0.2, curve=curve.linear)
            hitbox=boxcast(origin=self.position+Vec3(0,0.8,0),direction=self.forward,distance=4.8,thickness=(2,3),ignore=[self,data.ground])
        else:
            hitbox=boxcast(origin=self.position+Vec3(0,0.8,0),direction=self.forward,distance=2.8,thickness=(2,3),ignore=[self,data.ground], debug= True)
        if hitbox.hit:
            self.apply_damage(hitbox.entity,self.attack*0.7+ data.last_attack_button[2]*1.30)
    
    def dash_attack(self):
        self.in_dash = False
        self.invulnerable = True
        invoke(setattr,self,'invulnerable',False,delay=0.3)
        hitbox_foward = boxcast(origin=self.position+Vec3(0,0.8,0),direction=self.forward,distance=1.8,thickness=(2.5,3),ignore=[self,data.ground])
        hitbox_back = boxcast(origin=self.position+Vec3(0,0.8,0),direction=self.back,distance=1.8,thickness=(2.5,3),ignore=[self,data.ground])
        if hitbox_foward.hit:
            self.apply_damage(hitbox_foward.entity,self.attack*1.2)
        elif hitbox_back.hit:
            self.apply_damage(hitbox_back.entity,self.attack*1.2)

    # dash function
    def dash(self):
        self.invulnerable = True
        self.animate('position', self.position+Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()*9.5, duration= 0.2, curve=curve.linear)
        invoke(setattr,self,'invulnerable',False,delay=0.2)
        invoke(setattr,self,'in_dash',True,delay=0.15)
        invoke(setattr,self,'in_dash',False,delay=0.3)
        self.running = True
        self.cooldowns[1] = time.process_time()+4
        
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
            if not getattr(entity,"in_combat"):
                entity.in_combat = True
            if getattr(entity, "target") is None:
                entity.target = self
            if not getattr(entity,"invulnerable"):
                entity.health -= damage - getattr(entity, "defense")

    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True
        
    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False
    
    #confirm that it won't hit anything
    def check_raycast(self):
        feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, ignore=(self,), distance=.5)
        head_ray = raycast(self.position+Vec3(0,self.height-.4,0), self.direction, ignore=(self,), distance=.5)
        chest_ray = raycast(self.position+Vec3(0,self.height/2,0), self.direction, ignore=(self,), distance=.5)
        if not feet_ray.hit and not head_ray.hit and not chest_ray:
            return True
    
    def walk(self):
        move_amount = self.direction * time.dt * self.speed*1.7 if self.running else self.direction * time.dt * self.speed 
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
        if self.actor.getCurrentAnim() in [
            'attack_back',
            'attack',
            'attack_left',
            'attack_forward',
            'attack_right',
        ]:
            self.actor.setH(180)
        else:
            angle = None
            if held_keys['w'] or held_keys['s']:
                angle = 180
            if held_keys['a'] and not held_keys['a']*held_keys['d']:
                angle = (270-held_keys['w']*45-held_keys['s']*135)
            if held_keys['d'] and not held_keys['a']*held_keys['d']:
                angle = (90+held_keys['w']*45+held_keys['s']*135)
            if angle != None:
                self.actor.setH(angle)
            
    def move_animation(self):
        orientation = (
            + held_keys['w'] * 'w'
            + held_keys['s'] * 's'
            + held_keys['a'] * 'a'
            + held_keys['d'] * 'd'
        )
        if self.actor.getCurrentAnim() in ['attack_back', 'attack', 'attack_left', 'attack_forward', 'attack_right']:
            if self.actor.getCurrentAnim() != data.animation_attack[f'{self.weapon}-{orientation[0]}']:
                self.actor.play(data.animation_attack[f'{self.weapon}-{orientation[0]}'],fromFrame=self.actor.getCurrentFrame())
        elif held_keys['s'] and not held_keys['w']:
            if self.actor.getCurrentAnim() != "walk_back" and not self.running:
                self.actor.loop("walk_back")
        elif held_keys['w']+held_keys['a']+held_keys['d']:
            if self.running and self.actor.getCurrentAnim() != "run":
                self.actor.loop('run')
            elif self.actor.getCurrentAnim() != "walk" and not self.running:
                self.actor.loop("walk")
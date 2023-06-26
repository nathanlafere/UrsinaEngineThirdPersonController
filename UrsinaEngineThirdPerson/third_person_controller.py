from ursina import *
import data
from panda3d import *
from direct.actor.Actor import Actor
import data


class ThirdPersonController(data.Character):
    def __init__(self, **kwargs):
        #self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        self.camera_pivot = Entity(y=150)
        camera.parent = self.camera_pivot
        camera.position = (0,10,-15)
        camera.rotation = (25,0,0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)
        self.inventory_itens = []
        #attributes
        self.attribute_points = 0
        self.attack = 1 + (self.str*60/100)
        self.defense = 1 + (self.vit*40/100)
        self.weapon = "bow"
        
        #state
        self.in_dash = False
        self.running = False
        self.cooldowns = [0,0,0]  #[0] basic attack, [1] dash, [2] spell attack
        
        for key, value in kwargs.items():
            setattr(self, key ,value)
        self.actor = Actor(data.player_model)
        self.actor.setH(180)
        self.actor.reparentTo(self)
        self.collider = BoxCollider(self,center=Vec3(0,0.85,0),size=(1,1.75,1))

    def update(self):
        self.gravity_update()
        self.camera_pivot.x,self.camera_pivot.z = self.x,self.z
        self.camera_pivot.y += (self.y+2 - self.camera_pivot.y) * time.dt * 5
        if held_keys['a']+held_keys['d']+held_keys['w']+held_keys['s']:
            self.rotateModel()
            self.move_animation()
        camera.position = clamp(camera.position,(0,1,-6),(0,13,-18))
        camera.rotation_x = clamp(camera.rotation_x, 7,31)
        # release cam
        if mouse.locked == True:
            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
            if held_keys['left alt']:
                self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -28, 80)
                self.camera_pivot.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
            else:
                self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -20, 50)
                self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                self.camera_pivot.rotation_y = self.rotation_y
        
        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()
        if mouse.moving and self.direction == 0 and self.actor.getH != 180:
            self.actor.setH(180)
        self.walk()

        if self.experience[0] >= self.experience[1]:
            self.raise_status()
            

    def input(self, key):
        
        if mouse.locked == True:
            if key == 'scroll down':
                camera.position += (0,1,-1)
                camera.rotation_x += 2
            elif key == 'scroll up':
                camera.position += (0,-1,1)
                camera.rotation_x -= 2
            if key == 'left mouse down':
                if self.in_dash:
                    self.dash_attack()
                elif self.cooldowns[0] < time.process_time():
                    if self.running:
                        self.speed -= 1.5
                        invoke(setattr,self,'speed',self.speed+1.5,delay=0.2)
                    self.cooldowns[0] = time.process_time() + 80*time.dt
                    self.combo_attack()
        
        if key == 'space':
            self.jump()
        
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
            hitbox=boxcast(origin=self.position+Vec3(0,0.8,0),direction=self.forward,distance=2.8,thickness=(2,3),ignore=[self,data.ground])
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
        
    #applies damage and some status changes after hitting something
    def apply_damage(self,entity,damage):
        if not hasattr(entity, "health"):
            return
        if not getattr(entity,"in_combat"):
            entity.in_combat = True
        if getattr(entity, "target") is None:
            entity.target = self
        if not getattr(entity,"invulnerable"):
            entity.health[0] -= damage - getattr(entity, "defense")
            if entity.health[0] <= 0:
                self.experience[0] += entity.experience
                data.interface.inventory.create_item(entity.random_loot())
        
    #confirm that it won't hit anything
    def check_raycast(self,direction):
        feet_ray = raycast(self.position+Vec3(0,0.45,0), direction, ignore=(self,), distance=.5)
        head_ray = raycast(self.position+Vec3(0,self.height-.4,0), direction,ignore=(self,), distance=.5)
        chest_ray = raycast(self.position+Vec3(0,self.height/2,0), direction, ignore=(self,), distance=.5)
        return feet_ray.hit or head_ray.hit or chest_ray.hit
    
    def walk(self):
        move_amount = self.direction * time.dt * self.speed*1.7 if self.running else self.direction * time.dt * self.speed
        if self.check_raycast(Vec3(1,0,0)):
            move_amount[0] = min(move_amount[0], 0)
        if self.check_raycast(Vec3(-1,0,0)):
            move_amount[0] = max(move_amount[0], 0)
        if self.check_raycast(Vec3(0,0,1)):
            move_amount[2] = min(move_amount[2], 0)
        if self.check_raycast(Vec3(0,0,-1)):
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
        elif held_keys['w']+held_keys['a']+held_keys['d'] and not held_keys['a']*held_keys['d']:
            if self.running and self.actor.getCurrentAnim() != "run":
                self.actor.loop('run')
            elif self.actor.getCurrentAnim() != "walk" and not self.running:
                self.actor.loop("walk")
    
    def raise_status(self):
        self.experience[0] = self.experience[0] - self.experience[1]
        self.experience[1] += self.experience[1]*30/100
        self.health[1] += 3
        self.mana[1] += 1.5
        self.attack += 0.5
        self.defense += 0.5
        self.attribute_points += 1
        self.health[0],self.mana[0] = self.health[1],self.mana[1]

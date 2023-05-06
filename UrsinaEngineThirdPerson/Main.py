from ursina import *
from panda3d import *
from direct.actor.Actor import Actor
import data
import enemy
import third_person_controller

app = Ursina()

def input(key):
    
    rotateModel()
    if key == 'escape':
        quit()
    if held_keys['left shift'] and any([held_keys['w'],held_keys['a'],held_keys['d']]) and not held_keys['s']:
        if not data.running:
            actor.loop('JinxRigAction.1')
        player.speed = 10
        data.running= True
    elif key in ['w up','a up','d up'] and not any([held_keys['w'],held_keys['a'],held_keys['d']]) or held_keys['s']:
        player.speed = 6
        data.running= False
        actor.stop()

def rotateModel():
    if held_keys['w'] or held_keys['s']:
        actor.setH(180)
    if held_keys['a']:
        actor.setH(270-held_keys['w']*45-held_keys['s']*135)
    elif held_keys['d']:
        actor.setH(90+held_keys['w']*45+held_keys['s']*135)
        

data.ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
Sky()
enemy_01 = enemy.Enemy(model='sphere',color=color.pink,health=50, rest_time=6)
player = third_person_controller.ThirdPersonController(collider="box")

actor = Actor("assets/Jinx.gltf")
myAnimControl = actor.getAnimControl('JinxRigAction.1')
actor.setH(180)
actor.reparentTo(player)

app.run()
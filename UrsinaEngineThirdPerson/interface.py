from ursina import *
import data
import itertools
import third_person_controller

class BaseInterface(Entity):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.inventory = Inventory()
        self.status_bar = StatusBar(player= self.player ,model='quad', parent=camera.ui, collider='box', position=Vec2(-0.738194, 0.415509), scale=(0.3,0.17), z=-1)
        self.status_tab = Entity(model='quad', parent=camera.ui, enabled=False, collider='box', position=Vec2(0.532407, 0.0462963), scale=(.3,0.27))
        self.action_bar = Entity(model='quad', parent=camera.ui, collider='box', position=Vec2(-0.296296,0.450074), scale=Vec2(0.45,0.1))
        self.ui_open_tabs = [self.status_bar, self.action_bar]
        self.held = None
    def update(self):
        #dragging ui
        if mouse.left:
            if self.held is None:
                if mouse.hovered_entity in self.ui_open_tabs+self.inventory.inventory_itens:
                    # managing tab layers
                    tab_clicked = self.inventory if mouse.hovered_entity in self.inventory.inventory_itens else mouse.hovered_entity
                    if self.ui_open_tabs[-1] != tab_clicked:
                        self.ui_open_tabs.remove(tab_clicked)
                        self.ui_open_tabs.append(tab_clicked)
                        for c in range(len(self.ui_open_tabs)):
                            self.ui_open_tabs[c].z = -(c+1)
                    if mouse.hovered_entity.parent == camera.ui:
                        self.held = [mouse.hovered_entity, Vec3(mouse.hovered_entity.position)-Vec3(mouse.position)]
                    else:
                        self.held = [mouse.hovered_entity, Vec3(mouse.hovered_entity.position)-Vec3(mouse.position)/Vec3(mouse.hovered_entity.parent.scale)]
                    self.held[0].collision = False
            else:
                drag(self.held)
        elif self.held != None:
            if (
                self.held[0] in self.inventory.inventory_itens
                and not self.inventory.hovered
                and mouse.hovered_entity not in self.inventory.inventory_itens
            ):
                destroy(self.held[0])
            self.held[0].collision = True
            self.held = None

    def input(self, key):
        if key == 'left control':
            mouse.locked = mouse.locked != True
        #open/close tabs
        if key == 'e':
            mouse.locked = self.inventory.enabled != False
            self.inventory.enabled = self.inventory.enabled != True
            self.ui_open_tabs.append(self.inventory) if self.inventory not in self.ui_open_tabs else self.ui_open_tabs.remove(self.inventory)
            self.inventory.z = -len(self.ui_open_tabs)
        if key == 'c':
            self.status_tab.enabled = self.status_tab.enabled != True
            self.ui_open_tabs.append(self.status_tab) if self.status_tab not in self.ui_open_tabs else self.ui_open_tabs.remove(self.status_tab)
            self.status_tab.z = -len(self.ui_open_tabs)
        if held_keys['alt'] and key == 'a':
            self.status_bar.enabled = self.status_bar.enabled != True
            self.ui_open_tabs.append(self.status_bar) if self.status_bar not in self.ui_open_tabs else self.ui_open_tabs.remove(self.status_bar)
            self.status_bar.z = -len(self.ui_open_tabs)
        if held_keys['alt'] and key == 'q':
            self.action_bar.enabled = self.action_bar.enabled != True
            self.ui_open_tabs.append(self.action_bar) if self.action_bar not in self.ui_open_tabs else self.ui_open_tabs.remove(self.action_bar)
            self.action_bar.z = -len(self.ui_open_tabs)

class Inventory(Entity):
    def __init__(self):
        super().__init__()
        self.inventory_itens = []
        self.inventory_slots = []
        self.model = 'quad'
        self.scale=(0.5,0.7)
        self.parent=camera.ui
        self.collider ='box'
        self.color = color.gray
        for c, l in itertools.product(range(12), range(9)):
            slot = Entity(model='quad',scale=(0.09,0.07), z=-0.1,parent=self, collider='box', color=color.dark_gray,position=Vec2(l*0.0948-0.374,-c*0.0733+0.37))
            self.inventory_slots.append(slot)
        
        self.enabled = False

class StatusTab():
    def __init__(self):
        super().__init__()

class StatusBar(Entity):
    def __init__(self, player, **kwargs):
        self.player = player
        super().__init__(**kwargs)
        self.health_bar = create_bar(self,Vec2(-0.025,0.2), model='assets/GZE_bar')
        self.mana_bar = create_bar(self,Vec2(-0.025,0.07), model='assets/GZE_bar')
        self.experience_bar = create_bar(self,Vec2(-0.025,-0.03),color.dark_gray,size=(0.72,.04))
    def update(self):
        update_bar(self.health_bar,self.player.health)
        update_bar(self.mana_bar,self.player.mana)
        update_bar(self.experience_bar,self.player.experience)


class Menu():
    def __init__(self):
        super().__init__()

def create_bar(_parent, pos, _color=None,size=(0.75,.06), border=False, model=None):
    if model is not None:
        return [Entity(model='quad', scale=size, texture=model, z=-0.1,parent=_parent, position=pos),
                Entity(model='quad', scale=size, texture='assets/gzeblue_mid', z=-0.2,parent=_parent, position=pos, color=_color, percent_text = '100%'),
                Entity(model='quad', scale=(0.018,size[1]), texture='assets/gzeblue_left', z=-0.3, parent=_parent, color=_color, position=pos+(-size[0]/2,0)),
                Entity(model='quad', scale=(0.018,size[1]), texture='assets/gzeblue_right', z=-0.4, parent=_parent, color=_color, position=pos+(size[0]/2,0))]
    if border:
        model = Quad(radius=0.16, aspect=10)
        Entity(model=model, scale=Vec2(size)+Vec2(size[1]*40/100,size[1]*40/100), color=color.gold, z=-0.1, parent=_parent, position=pos)
    return [Entity(model='quad', scale=size, color=color.gray, z=-0.2, parent=_parent, position=pos, percent_text = '100%'),Entity(model='quad', scale=size, color=_color, z=-0.3, parent=_parent, position=pos)]

def update_bar(bar,values):
    bar[1].scale_x = bar[0].scale_x*(values[0]*100/values[1])/100
    bar[1].x = bar[0].x +(bar[1].scale_x - bar[0].scale_x)/2
    if len(bar) > 2:
        if values[0] > 0:
            bar[3].x = bar[1].x+bar[1].scale[0]/2
        bar[1].enabled = values[0] > 0
        bar[2].enabled = values[0] > 0
        bar[3].enabled = values[0] > 0

def drag(held):
    if held[0].parent == camera.ui:
        held[0].position = Vec2(mouse.x,mouse.y) + held[1]
    else:
        held[0].position = Vec2(mouse.x,mouse.y)/Vec2(held[0].parent.scale_x,held[0].parent.scale_y) + held[1]

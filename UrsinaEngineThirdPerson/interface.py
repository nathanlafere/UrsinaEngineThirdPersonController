from ursina import *
import data
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
                    self.held = [mouse.hovered_entity,mouse.hovered_entity.position-mouse.position]
                    self.held[0].collision = False
            else:
                drag(self.held)
        elif self.held != None:
            if self.held[0] in self.inventory.inventory_itens and not self.inventory.hovered :
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
        self.model='quad'
        self.parent=camera.ui
        self.color= color.red
        self.collider ='box'
        self.button = Button(text='click me!',highlight_color=color.dark_gray,scale=(0.1,0.1), text_color=color.white, parent=self)
        self.button.on_click = self.clicked
        a=Entity(model='quad', parent=self, color=color.black, scale=Vec2(0.1,0.1), collider='box')
        self.inventory_itens = [self.button,a]
        self.enabled = False
        
    def clicked(self):
        print(self)

class StatusTab():
    def __init__(self):
        super().__init__()

class StatusBar(Entity):
    def __init__(self, player, **kwargs):
        self.player = player
        super().__init__(**kwargs)
        self.health_bar = create_bar(self,Vec2(-0.025,0.18),_color=color.green, border=True)
        self.mana_bar = create_bar(self,Vec2(-0.025,0.08),_color=color.blue, border=True)
        self.experience_bar = create_bar(self,Vec2(-0.025,-0.005),(0.72,.04),_color=color.dark_gray)
    def update(self):
        update_bar(self.health_bar,self.player.health)
        update_bar(self.mana_bar,self.player.mana)
        update_bar(self.experience_bar,self.player.experience)


class Menu():
    def __init__(self):
        super().__init__()

def create_bar(_parent, pos, size=(0.75,.06), _color=color.blue, border=False):
    if border:
        # middle border
        Entity(model='quad', scale=size+(.02,.028), color=color.gold, parent=_parent, position=pos)
        # right border
        Entity(model='quad', scale=size+(-.71,+.003), color=color.gold, parent=_parent, position=pos+Vec2(0.378,0))
        Entity(model='quad', scale=size+(-.71,+.018), color=color.gold, parent=_parent, position=pos+Vec2(0.373,0))
        Entity(model='quad', scale=size+(-.71,+.028), color=color.gold, parent=_parent, position=pos+Vec2(0.37,0))
        # left border
        Entity(model='quad', scale=size+(-.71,+.003), color=color.gold, parent=_parent, position=pos-Vec2(0.378,0))
        Entity(model='quad', scale=size+(-.71,+.018), color=color.gold, parent=_parent, position=pos-Vec2(0.373,0))
        Entity(model='quad', scale=size+(-.71,+.028), color=color.gold, parent=_parent, position=pos-Vec2(0.37,0))
    return [Entity(model='quad', scale=size, color=color.gray, parent=_parent, position=pos),Entity(model='quad', scale=size, color=_color, parent=_parent, position=pos, percent_text = '100%')]

def update_bar(bar,values):
    bar[1].scale_x = bar[0].scale_x*(values[0]*100/values[1])/100
    bar[1].x = bar[0].x +(bar[1].scale_x - bar[0].scale_x)/2

def drag(held):
    held[0].position = mouse.position + held[1]

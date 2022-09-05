
import os
import sys
#import json
import yaml

import ui
import photos
import console
import dialogs
from objc_util import ObjCInstance

def randcol():
    import random
    return (random.random(),random.random(),random.random())

sys.path.append('.')
from print_override import print
import layoutios

# static variable : view name
BUTTON_CLOSE = 'close_button'

VIEW_MSV = 'main_scrollview'
VIEW_MIV = 'main_imageview'

VIEW_THUMB = 'thumbnail_view'

VIEW_ALBUM = 'albums_scroll_view'

VIEW_BUTTON_BG = 'controller_bg_view'
BUTTON_NEXT = 'next_button'
BUTTON_PREV = 'prev_button'
BUTTON_MENU = 'menu_button'

COUNTER_VIEW = 'counter'

with open('preferences.yaml') as f:
    CONFIG = yaml.safe_load(f)

class image_view_controller():
    def __init__(self, view, assets, left=None, right=None, scale='fill'):
        self.left  = left
        self.right = right
        self.view = view
        self.__assets = assets
        
        # self.size = [view.height, view.width]
        
        self.view.content_mode = ui.CONTENT_SCALE_ASPECT_FIT if scale == 'fit' else ui.CONTENT_SCALE_ASPECT_FILL
    
    @property
    def assets(self):
        return self.__assets
    
    @assets.setter
    def assets(self, assets):
        self.__assets = assets
        if self.left is not None:
            self.left.assets = assets
        if self.right is not None:
            self.right.assets = assets
    
    def set_image(self, index, crop=False):
        # size = [int(self.view.width), int(self.view.height)]
        size = (64, 64)
        if 0 <= index < len(self.assets):
            if crop:
                self.view.image = self.assets[index].get_ui_image(size, crop=True)
            else:
                self.view.image = self.assets[index].get_ui_image((1024, 1024))
            if self.left is not None:
                self.left.set_image(index - 1, crop=True)
            if self.right is not None:
                self.right.set_image(index + 1, crop=True)
        else:
            self.view.image = None

class sta_photo_distributor_v2():
    def __init__(self, v):
        self.v = v
        
        self.__index = 0
        self.update_assets()
        self.update_albums()
        self.MIVC = image_view_controller(
            self.v[VIEW_MSV][VIEW_MIV],
            self.assets,
            scale='fit'
        )
        
        self.view_size = (
            self.v[VIEW_MSV].width,
            self.v[VIEW_MSV].height
        )
        
        self.__delete_mode = False
    
    def awake(self):
        # button function setting
        self.v[BUTTON_CLOSE].action = self.on_button_close
        self.v[VIEW_BUTTON_BG][BUTTON_NEXT].action = self.on_button_next
        self.v[VIEW_BUTTON_BG][BUTTON_PREV].action = self.on_button_prev
        self.v[VIEW_BUTTON_BG][BUTTON_MENU].action = self.on_button_menu
        
        # Thumbnail setting
        self.TB = thumbnails_view(self.v[VIEW_THUMB], 7)
        self.TB.create_views(self.assets)
        self.TB.top_thumbnail.set_image(self.index, crop=True)
        
        # slide view setting
        self.v[VIEW_MSV].content_size = self.view_size
        self.v[VIEW_MSV].always_bounce_horizontal = True
        self.v[VIEW_MSV].always_bounce_vertical = True
        
        self.AV = album_buttons_view(self.v[VIEW_ALBUM], self.on_button_select_album)
        
        # counter setting
        ObjCInstance(self.v[COUNTER_VIEW]).clipsToBounds = True
        self.v[COUNTER_VIEW].background_color = (1,1,1,0.6)
        
        # menu bar setting
        self.v[VIEW_BUTTON_BG].background_color = (1,1,1,0.8)
        
        self.open_last_image()
    
    def start(self):
        pass
        
    def update_assets(self):
        self.assets = photos.get_assets()
        try:
            self.MIVC.assets = self.assets
        except AttributeError:
            pass
        try:
            self.TB.top_thumbnail.assets = self.assets
        except AttributeError:
            pass
    
    def update_albums(self):
        self.albums = photos.get_albums()
    
    def open_image(self):
        self.MIVC.set_image(self.index)
        id = self.assets[self.index].local_id
        with open(CONFIG['PATH_PREV_ID'], 'w') as f:
            f.write(id)
        self.TB.top_thumbnail.set_image(self.index, crop=True)
        
        self.v[COUNTER_VIEW].text = f'{self.index+1}/{len(self.assets)} ({len(self.assets)-self.index-1})'
    
    @property
    def index(self):
        return self.__index
    @index.setter
    def index(self, index):
        if not 0 <= index < len(self.assets):
            print('Index is out of assets length')
        self.__index = index
        self.open_image()
    
    @property
    def delete_mode(self):
        return self.__delete_mode
    
    @delete_mode.setter
    def delete_mode(self, value):
        self.__delete_mode = value
        self.v[VIEW_ALBUM].background_color = (1, 0.3, 0.3) if self.__delete_mode else None
    
    def next_image(self):
        if self.index >= len(self.assets)-1:
            print('これ以上進めません。')
        else:
            self.index += 1
    
    def prev_image(self):
        if self.index < 0 + 1:
            print('これ以上戻れません。')
        else:
            self.index -= 1
    
    def pick_image(self):
        asset = photos.pick_asset(self.assets)
        if asset is None:
            pass
        else:
            id = asset.local_id
            index = [asset.local_id for asset in self.assets].index(id)
            self.index = index
    
    def open_last_image(self):
        if os.path.exists(CONFIG['PATH_PREV_ID']):
            with open(CONFIG['PATH_PREV_ID']) as f:
                id = f.read().split()[0]
            try:
                index = [asset.local_id for asset in self.assets].index(id)
                self.index = index
                return
            except ValueError:
                pass
        if not self.open_from_prev_openings():
            self.pick_image()
    
    def open_from_prev_openings(self):
        if os.path.exists(CONFIG['PATH_PREV_IDs']):
            with open(CONFIG['PATH_PREV_IDs']) as f:
                ids = f.read().split()
            for id in ids:
                try:
                    index = [asset.local_id for asset in self.assets].index(id)
                    self.index = index
                    return True
                except ValueError:
                    continue
            
            return False
            
    
    def change_del_mode(self):
        self.delete_mode = not self.delete_mode
    
    def add_to_album(self, sender):
        album_name = sender.name
        index = [a.title for a in self.albums].index(album_name)
        self.albums[index].add_assets([self.assets[self.index]])
        console.hud_alert(f'add to {album_name}', duration=0.5)
        
        self.next_image()
    
    def del_from_album(self, sender):
        album_name = sender.name
        index = [a.title for a in self.albums].index(album_name)
        self.albums[index].remove_assets([self.assets[self.index]])
        console.hud_alert(f'remove from {album_name}', duration=0.5)
        
        self.delete_mode = False
        
    
    def delete_current(self):
        try:
            photos.batch_delete([self.assets[self.index]])
            self.update_assets()
            self.open_image()
        except IOError:
            print('faild to del photo')
    
    def on_button_close(self, sender):
        ids = [a.local_id for a in self.assets[:self.index+1]]
        ids.reverse()
        with open(CONFIG['PATH_PREV_IDs'], 'w') as f:
            f.write('\n'.join(ids))
        self.v.superview.close()

    def on_button_next(self, sender):
        self.next_image()
    
    def on_button_prev(self, sender):
        self.prev_image()
    
    def on_button_menu(self, sender):
        option = console.alert('Menu', 
            button1='画像を選択',
            button2='アルバムから削除',
            button3='端末から削除',
            hide_cancel_button=True
        )
        if option == 1:
            self.pick_image()
        if option == 2:
            self.change_del_mode()
        if option == 3:
            self.delete_current()
    
    def on_button_select_album(self, sender):
        if self.delete_mode:
            self.del_from_album(sender)
        else:
            self.add_to_album(sender)

class thumbnails_view():
    def __init__(self, view, count):
        if count % 2 == 0:
            raise ValueError('Must Odd Number')
        
        self.view = view
        self.count = count
    
    def reset_views(self):
        for viewcon.view in self.thumb_view_cons:
            self.view.remove_subview(viewcon.view)
        self.set_views()
    
    def set_views(self):
        isHorizontal = self.view.width > self.view.height
        
        x = 0
        for viewcon in self.thumb_view_cons:
            viewcon.view.center = self.view.center
            if isHorizontal:
                viewcon.view.x = x
            else:
                viewcon.view.y = x
            x += viewcon.view.width
            self.view.add_subview(viewcon.view)
    
    def create_views(self, assets):
        isHorizontal = self.view.width > self.view.height
        
        if isHorizontal:
            size = int(self.view.width / self.count)+1
        else:
            size = int(self.view.height / self.count)+1
        
        self.thumb_view_cons = []
        l = image_view_controller(ui.ImageView(flex='LRTB'), assets)
        r = image_view_controller(ui.ImageView(flex='LRTB'), assets)
        l.view.width, l.view.height = size, size
        r.view.width, r.view.height = size, size
        self.thumb_view_cons[0:0] = [l, r]
        for i in range(1, int(self.count/2)):
            l = image_view_controller(ui.ImageView(flex='LRTB'), assets,left=self.thumb_view_cons[i-1])
            r = image_view_controller(ui.ImageView(flex='LRTB'), assets, right=self.thumb_view_cons[i])
            l.view.width, l.view.height = size, size
            r.view.width, r.view.height = size, size
            self.thumb_view_cons[i:0] = [l, r]
        c = image_view_controller(ui.ImageView(flex='LRTB'), assets, left=self.thumb_view_cons[int(self.count/2)-1], right=self.thumb_view_cons[int(self.count/2)])
        c.view.width, c.view.height = size, size
        c.view.border_width = 2
        c.view.border_color = (0, 1, 0)
        self.thumb_view_cons[int(self.count/2):0] = [c]
        self.top_thumbnail = c
        self.set_views()

class album_buttons_view():
    def __init__(self, view, button_function):
        self.view = view
        
        self.buttons = []
        all_asset_collections = photos.get_albums()
        asset_collections = []
        for i, mask in enumerate(CONFIG['ALBUM_MASK']):
            if mask == 1:
                try:
                    asset_collections.append(all_asset_collections[i])
                except IndexError:
                    break
        if CONFIG['ALBUM_MASK'][-1] == 1:
            asset_collections.extend(all_asset_collections[len(CONFIG['ALBUM_MASK']):])
        for ac in asset_collections:
            name = ac.title
            button = ui.Button()
            button.action = button_function
            button.bounds = (0, 0, 48, 48)
            button.corner_radius = 24
            button.background_color = (0.9,0.9,0.9,0.9)
            button.name = name
            if name.startswith('$'):
                button.title = name[1]
            else:
                button.title = name[0]
            self.buttons.append(button)
        
        width = len(self.buttons) * (self.buttons[0].width + 8) + 8
        height = self.view.content_size[1]
        if width > self.view.width:
            self.view.content_size = (width, height)
            padding = 8
        else:
            self.view.content_size = (self.view.width, height)
            padding = (self.view.width - len(self.buttons) * self.buttons[0].width) / (len(self.buttons) + 1)

        x = padding
        for button in self.buttons:
            button.center = (0, self.view.height/2)
            button.x = x
            self.view.add_subview(button)
            
            x += button.width + padding

def remove_splash():
    def animation():
        sv['splash'].alpha = 0.0
    def completion():
        sv.remove_subview(sv['splash'])
    ui.animate(animation, 0.2, 0.0, completion)
    
sv = ui.View(frame=(0, 0, 512, 512))

v = ui.load_view()
v.flex = 'WH'
sv.add_subview(v)
statusbar = 44 if layoutios.notch else 20
statusbar += 200 if CONFIG["IS_WITH_PIP"] else 0
homebar = 34 if layoutios.homebar else 0
v.height -= statusbar
v.y      += statusbar
v.height -= homebar

splash = ui.View(
    frame=(0, 0, 512, 512),
    flex='WH',
    background_color='skyblue',
    name='splash'
)
splash.touch_enabled = False
sv.add_subview(splash)

sv.present(
    'fullscreen',
    hide_title_bar=True,
    orientations=['portrait', 'portrait-upside-down']
)

SPD2 = sta_photo_distributor_v2(v)
SPD2.awake()

remove_splash()

SPD2.start()

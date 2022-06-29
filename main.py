
import os
import sys
import json

import ui
import photos

def randcol():
    import random
    return (random.random(),random.random(),random.random())

sys.path.append('.')
from print_override import print

# static variable : view name
BUTTON_CLOSE = 'close_button'

VIEW_MSV = 'main_scrollview'
VIEW_MIV = 'main_imageview'

VIEW_THUMB = 'thumbnail_view'

VIEW_ALBUM = 'albums_scroll_view'

VIEW_BUTTON_BG = 'controller_bg_view'
BUTTON_NEXT = 'next_button'
BUTTON_PREV = 'prev_button'
BUTTON_SELECT = 'select_button'

with open('preferences.json') as f:
    CONFIG = json.load(f)

class image_view_controller():
    def __init__(self, view, assets, left=None, right=None, scale='fill'):
        self.left  = left
        self.right = right
        self.view = view
        self.assets = assets
        
        # self.size = [view.height, view.width]
        
        self.view.content_mode = ui.CONTENT_SCALE_ASPECT_FIT if scale == 'fit' else ui.CONTENT_SCALE_ASPECT_FILL
    
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
        self.MIVC = image_view_controller(
            self.v[VIEW_MSV][VIEW_MIV],
            self.assets,
            scale='fit'
        )
        
        self.view_size = (
            self.v[VIEW_MSV].width,
            self.v[VIEW_MSV].height
        )
    
    def awake(self):
        # button function setting
        self.v[BUTTON_CLOSE].action = self.on_button_close
        self.v[VIEW_BUTTON_BG][BUTTON_NEXT].action = self.on_button_next
        self.v[VIEW_BUTTON_BG][BUTTON_PREV].action = self.on_button_prev
        self.v[VIEW_BUTTON_BG][BUTTON_SELECT].action = self.on_button_select
        
        # Thumbnail setting
        self.TB = thumbnails_view(self.v[VIEW_THUMB], 7)
        self.TB.create_views(self.assets)
        self.TB.top_thumbnail.set_image(self.index, crop=True)
        
        # slide view setting
        self.v[VIEW_MSV].content_size = self.view_size
        self.v[VIEW_MSV].always_bounce_horizontal = True
        self.v[VIEW_MSV].always_bounce_vertical = True
        
        self.open_last_image()
    
    def start(self):
        pass
        
    def update_assets(self):
        self.assets = photos.get_assets()
    
    def open_image(self):
        self.MIVC.set_image(self.index)
        id = self.assets[self.index].local_id
        with open(CONFIG['PATH_PREV_ID'], 'w') as f:
            f.write(id)
        self.TB.top_thumbnail.set_image(self.index, crop=True)
    
    @property
    def index(self):
        return self.__index
    @index.setter
    def index(self, index):
        if not 0 <= index < len(self.assets):
            print('Index is out of assets length')
        self.__index = index
        self.open_image()
    
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
        
        self.pick_image()
    
    def on_button_close(self, sender):
        self.v.superview.close()

    def on_button_next(self, sender):
        self.next_image()
    
    def on_button_prev(self, sender):
        self.prev_image()
    
    def on_button_select(self, sender):
        self.pick_image()

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
        self.thumb_view_cons[int(self.count/2):0] = [c]
        self.top_thumbnail = c
        self.set_views()

def remove_splash():
    def animation():
        sv['splash'].alpha = 0.0
    def completion():
        sv.remove_subview(sv['splash'])
    ui.animate(animation, 0.2, 0.0, completion)
    
sv = ui.View(frame=(0, 0, 512, 512))

v = ui.load_view()
v.flex = 'WH'
splash = ui.View(
    frame=(0, 0, 512, 512),
    flex='WH',
    background_color='skyblue',
    name='splash'
)
splash.touch_enabled = False
sv.add_subview(v)
v.height -= CONFIG['STATUS_BAR_HEIGHT']
v.y      += CONFIG['STATUS_BAR_HEIGHT']
sv.add_subview(splash)

sv.present('fullscreen', hide_title_bar=True)

SPD2 = sta_photo_distributor_v2(v)
SPD2.awake()

remove_splash()

SPD2.start()

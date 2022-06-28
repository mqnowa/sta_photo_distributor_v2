import ui
import sys

import photos

sys.path.append('.')

from print_override import print

v = ui.load_view()
v.present('sheet')

class sta_photo_distributor_v2():
    def __init__(self, v):
        self.v = v
        
        self.__index = 0
        self.update_assets()
        
    def update_assets(self):
        self.assets = photos.get_assets()
    
    def open_image(self):
        pass
    
    @property
    def index(self):
        return self.__index
    @index.setter
    def index(self, index):
        if not 0 <= index < len(self.assets):
            raise IndexError('Index Error')
        self.__index = index
        self.open_image()
    
    def next_image(self):
        self.index = self.__index + 1
    
    def prev_image(self):
        self.index = self.__index - 1

class image_view_controller():
    def __init__(self, view, assets, left=None, right=None):
        self.left  = left
        self.right = right
        self.view = view
        self.assets = assets
        
        self.size = [view.height, view.width]
    
    def set_image(self, index):
        if 0 <= index < len(self.assets):
            view.image = self.assets[index].get_ui_image(self.size, crop=True)
            if self.left is not None:
                left.set_image(index - 1)
            if self.right is not None:
                right.setimgee(index + 1)

print('a')

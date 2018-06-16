# -*- coding: utf-8 -*-
"""
Created on Fri May 11 14:08:24 2018

@author: hsamant
"""
import os, sys
from PIL import Image
import pdb
import numpy as np

g_tile_size = 20    # size of tiles in pixel for length and height
g_allowable_lh_ratio = 0.5  # if tile images have ratio of dimensions lesser  than this then that imageis descarded
g_tiles_per_row = 50  # number of tiles in each row. Higher this number, better the resolution

class Tiles:
    def __init__(self,tiles_folder_path):
        self.tiles_folder_path = tiles_folder_path
        
    def get_tiles(self):
        l_processed_tiles = []
        l_original_tiles =  []
        
        for root, subFolders, files in os.walk(self.tiles_folder_path):
            for tile in files:
                if tile.endswith('jpg'):
                    tile_path  = os.path.join(root, tile)
                    img = Image.open(tile_path)
                    
                    processed_image = self.process_image(img)
                    
                    if processed_image:
                        l_processed_tiles.append(processed_image)
                        l_original_tiles.append(img)
                    
        return l_original_tiles, l_processed_tiles
                    
    def process_image(self,img):
        #1 Make sure tile is square. If not square then following
        ### if l/h  or h/l ratio is less than g_allowable_lh_ratio then skip that image
        l,h = img.size
        
        if l/h < g_allowable_lh_ratio or h/l < g_allowable_lh_ratio:
            img = None
        else:
            img = self.tile_square(img)
            
        return img
    
    def tile_square(self, img):
        l,h = img.size
        
        try:
            if l/h == 1.0 :
                img1=  img.resize((g_tile_size, g_tile_size))
            elif l > h:
                l_new = int(l / h * g_tile_size)
                img1 = img.resize((l_new,g_tile_size))
                l_crop = int((l_new - g_tile_size )/2)
                img1 = img1.crop((l_crop,0,l_new-l_crop,g_tile_size))
                img1 = img1.resize((g_tile_size,g_tile_size))
            elif l < h:
                h_new = int(h / l * g_tile_size)
                img1 = img.resize((g_tile_size,h_new))
                h_crop = int((h_new - g_tile_size )/2)
                img1 = img1.crop((0,h_crop,g_tile_size,h_new-h_crop))
            
            return img1
        except:
            return None
        
class BaseImage:
    def __init__(self,sBaseImagePath):
        self.sBaseImagePath = sBaseImagePath
        
    def imageResize(self):
        img = Image.open(self.sBaseImagePath)
        l,h = img.size
        
        try:
            if l/h == 1.0 :
                img1=  img.resize((g_tile_size * g_tiles_per_row , g_tile_size  * g_tiles_per_row))
            elif l > h:
                l_crop = int((l - h )/2)
                img1 = img.crop((l_crop,0,l-l_crop,h))
                img1 = img.resize((g_tile_size * g_tiles_per_row , g_tile_size  * g_tiles_per_row))
            elif l < h:
                h_crop = int((h - l )/2)
                img1 = img.crop((0,h_crop,l,h-h_crop))
                img1 = img.resize((g_tile_size * g_tiles_per_row , g_tile_size  * g_tiles_per_row))
                
            return img1
        except:
            return None
        
class TilePlacement:
    def __init__(self, l_tiles, i_baseImage):
        self.l_tiles = l_tiles
        self.i_baseImage = i_baseImage
        # code to check dimentions of tiles and base image. if error raise exception
        
    def checkDimensions(self):
        # will return 1 if all tile sizes and base image size is square and integral multiple
        return 1
    
    def getDiff(self,i_base,i_tile):
        rgb_base = i_base.getdata()
        rgb_tile = i_tile.getdata()
        diff = 0
        for i in range(g_tile_size^2 -1):
                diff = diff + ((rgb_base[i][0] - rgb_tile[i][0]) ^ 2 +
                        (rgb_base[i][1] - rgb_tile[i][1]) ^ 2 +
                        (rgb_base[i][2] - rgb_tile[i][2]) ^ 2 )
                
        return diff
    
    def getTilePlacement(self):
        l_indexed_tiles = []
        arr_indexed_tiles = np.zeros((g_tiles_per_row, g_tiles_per_row))
        for l in range(g_tiles_per_row):
            for h in range(g_tiles_per_row):
                max_diff = sys.float_info.max
                for i in range(len(self.l_tiles)):
                    base_lh = self.i_baseImage.crop((l * g_tile_size, h * g_tile_size,
                                               l * g_tile_size + 49, h * g_tile_size + 49))
                    tile = self.l_tiles[i]
                    diff = self.getDiff(base_lh,tile)
                    
                    if diff < max_diff:
                        max_diff = diff
                        matched_tile_index = i
                 
                l_index = (l,h,matched_tile_index)
                l_indexed_tiles.append(l_index)
                arr_indexed_tiles[l,h] = matched_tile_index
        
        return arr_indexed_tiles
    
class Mosaic:
    def __init__(self,a_index,l_proc_image):
        self.a_index = a_index
        self.l_proc_image = l_proc_image
        
    def generateMosaic(self):
        iMosaic = Image.new('RGB',(g_tile_size * g_tiles_per_row,g_tile_size * g_tiles_per_row))
        for l in range(g_tiles_per_row):
            for h in range(g_tiles_per_row):
                iMosaic.paste(l_proc_images[int(a_index[l][h])],
                                            (l * g_tile_size, h * g_tile_size))
        return iMosaic
            
                    
if __name__ == '__main__':
    pdb.set_trace()
    _, l_proc_images = Tiles('/Volumes/DataSci/Data/HSCode/PhotoMosaic/Obama').get_tiles()
    baseImage = BaseImage('/Volumes/DataSci/Data/HSCode/PhotoMosaic/ObamaBase.jpg').imageResize()
    a_index = TilePlacement(l_proc_images,baseImage).getTilePlacement()
    i_Mosaic = Mosaic(a_index,l_proc_images).generateMosaic()
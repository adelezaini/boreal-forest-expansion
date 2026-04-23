###### This python file collects fuctions to modify PFT configuration, such as in surfdata_map file

####### Import packages
import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap,LinearSegmentedColormap

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
# To choose hex colors. https://xkcd.com/color/rgb/
# To pick the hex color with a pen on the picture: https://imagecolorpicker.com/en

def hex_to_rgb(value):
    #Author: Kerry Halupka
    #https://towardsdatascience.com/beautiful-custom-colormaps-with-matplotlib-5bab3d1f0e72
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values'''
    value = value.strip("#") # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def sequential_colormap(hex_value, hex_value2 = '#ffffff', reversed = False): #'#0a5f38'
    # Adapted from:
    #https://towardsdatascience.com/creating-colormaps-in-matplotlib-4d4de78a04b8
    rgb_values = hex_to_rgb(hex_value)
    colors = np.ones((256, 4))
    
    for i in range(3):
        if not reversed:
            colors[:, i] = np.linspace(hex_to_rgb(hex_value2)[i]/256, hex_to_rgb(hex_value)[i]/256, 256)
        else:
            colors[:, i] = np.linspace(hex_to_rgb(hex_value)[i]/256, hex_to_rgb(hex_value2)[i]/256, 256)
    
    return ListedColormap(colors)


def diverging_colormap(hex_value1, hex_value2, hex_value3 = '#ffffff'):
    #https://towardsdatascience.com/creating-colormaps-in-matplotlib-4d4de78a04b8
    
    cmp1 = sequential_colormap(hex_value1, hex_value3, reversed=True)
    cmp2 = sequential_colormap(hex_value2, hex_value3, reversed=True)
    
    colors = np.vstack((cmp1(np.linspace(0, 1, 128)),cmp2(np.linspace(1, 0, 128))))
    
    return ListedColormap(colors)
    
    
    
    

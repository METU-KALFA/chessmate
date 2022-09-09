import json
import sys
import os
import random
from PIL import Image
import numpy as np
import cv2 as cv

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision import transforms
from torch.autograd import Variable
import torch.optim as optim

# defining the main training and optimization parameters
imageSize=[1200,800]
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
BATCH_SIZE = 40

# path variables => can be handy
# DATA_PATH (string)
#   |-> relative data location from board directory
DATA_PATH = '../../data/'
# GIVEN_PATH (string) can be <"train", "val", "test">
#   |-> chooses the directory to load the data from
#GIVEN_PATH = "train"

# count of files and file names
#   |-> due to large amount of data, 
#       files be loaded to memory as batches
#   |-> since file names are NOT ordered starting from 0
#       it's NOT enough to store the count of files
train_file_count = -1
train_files = []

val_file_count = -1
val_files = []

test_file_count = -1
test_files = []

img_dict = {}
corner_dict = {}

# getFileCount => output:
#                        file_count (int)  
#
#              => saves the file names without file-extension parts  
#              => saves the file count
def getFileCount():
    # get the global variables
    global train_file_count, train_files
    # relative path to given_path
    current_path = DATA_PATH + "train/"
    # get the list of file names in the current_path 
    train_files = [x[:-4] for x in os.listdir(current_path) if x.endswith('.png')]
    train_file_count = len(train_files)
    
    global val_file_count, val_files
    # relative path to given_path
    current_path = DATA_PATH + "val/"
    # get the list of file names in the current_path 
    val_files = [x[:-4] for x in os.listdir(current_path) if x.endswith('.png')]
    val_file_count = len(val_files)
    
    
    global test_file_count, test_files
    # relative path to given_path
    current_path = DATA_PATH + "test/"
    # get the list of file names in the current_path 
    test_files = [x[:-4] for x in os.listdir(current_path) if x.endswith('.png')]
    test_file_count = len(test_files)

    return (train_file_count, val_file_count, test_file_count)

# dataLoader => output:
#                      load_success (bool)   
#                          |-> return True if load operation succeeded
#                          |-> return False otherwise   
# 
#            => saves the images(as numpy array) in the batch into img_dict
#            => saves the corner points of the board into corner_dict
def dataLoader(type, low = 0):
    # pre-set the return value
    load_success = False
    # relative path to given_path
    current_path = DATA_PATH + type +'/'
    
    # get the corresponding file names
    if(type == "train"):
        limit = (low+BATCH_SIZE) if (low+BATCH_SIZE - 1) < file_count else file_count
        file_names = train_files[low:limit]
    if(type == "val"):
        limit = (low+BATCH_SIZE) if (low+BATCH_SIZE - 1) < file_count else file_count
        file_names = val_files[low:limit]
    if(type == "test"):
        limit = (low+BATCH_SIZE) if (low+BATCH_SIZE - 1) < file_count else file_count
        file_names = test_files[low:limit]
        
    # clean the previously loaded data
    img_dict.clear()
    corner_dict.clear()
    
    try:
        # load the new set of data
        for i in file_names:
            # load the current image
            img_path = current_path + i + '.png'
            cur_img = np.asarray(Image.open(img_path))
            img_dict[i] = cur_img

            # load the current image's corner points
            json_path = current_path + i + '.json'
            with open(json_path) as f:
                data = json.load(f)
            corner_dict[i] = data['corners']
        load_success = True
        return load_success
    except:
        print("FILE LOADING ERROR")
        return load_success

# drawMinAreaRect => input:
#                          img (np.array)
#                              |-> given image to draw corner and lines on 
#                          corners (list of list) 
#                              |-> corners list, size of 4 <2 element list>
#                          corner_color (tuple) 
#                              |-> color of the corners to be drawn 
#                          corner_radius (int) 
#                              |-> radius of the corners to be drawn
#                          line_color (tuple)
#                              |-> color of the edges to be drawn      
#                          line_thickness (int)
#                              |-> thickness of the edges to be drawn
#                   output:
#                          drawn_img (Image)
#                              |-> the image after corners and edges drawn on it   
# #
def drawMinAreaRect(img, corners, corner_color = (0,255,0), corner_radius = 10, line_color = (255,0,0), line_thickness = 10):
    for corner in corners:
        img = cv.circle(img, (corner[0], corner[1]), radius=corner_radius, color=corner_color, thickness=-1)
            
    for i in range(4):
        img = cv.line(img, corners[i%4], corners[(i+1)%4], color=line_color, thickness=line_thickness)

    #img = Image.fromarray(img)
    return img

def drawBoundingBox(img, corners, line_color = (0,0,255), line_thickness = 10):
    xx = [corner[0] for corner in corners]
    yy = [corner[1] for corner in corners]
    [minx, maxx] = min(xx), max(xx)
    [miny, maxy] = min(yy), max(yy)
    corners = [[minx,miny], [minx, maxy], [maxx, maxy], [maxx, miny]]
    for i in range(4):
        img = cv.line(img, corners[i%4], corners[(i+1)%4], color=line_color, thickness=line_thickness)
    return img

# drawContour => input:
#                      count (int)
#                          |-> number of images to draw contour on 
#                      save (bool)
#                          |-> save the image after drawing the contour TODO change this to location for saving(if none do not save)
# # 
def drawContour(count = 1, save = True):
    if count < 1:
        print("INVALID ARGUMENT :: count < 1 is not acceptable!")
        return
    else:
        file_names = random.sample(list(img_dict.keys()), count)
        for (name, idx) in zip(file_names, range(count)):
            print(name)
            cur_img = img_dict[name]
            cur_corners = corner_dict[name]
            cur_img = drawBoundingBox(cur_img, cur_corners)
            cur_img = drawMinAreaRect(cur_img, cur_corners)

            img = Image.fromarray(cur_img)
            img.save(f"{idx}""_rectBB.png")
    
# train_model => input:
#                      version (char) can be <'n', 's', 'm', 'l', 'x'> 
#                      |-> version of the yolov5 to be used 
# 
# 
# 
# 
# #
def train_model(version = 'l'):
    model = torch.hub.load('ultralytics/yolov5', 'yolov5' + version, pretrained=True)
    img = []
    result = model(img)
    result.print()

#
# 
# #
def test_model():
    imgs = []


# setArgs => input:
#                  argv (list)
#                      |-> argument vector
#         => sets the varibles according to given arguments from command line  
def setArgs(argv):
    pass
    #global GIVEN_PATH
    #GIVEN_PATH = argv[0]

if __name__ == "__main__":
    # if any given arg, set the args
    if len(sys.argv) > 1:
        setArgs(sys.argv[1:])

    # save fie names and file count
    (c_train, c_val, c_test) = getFileCount()


    # load image and corner data 
    dataLoader()
    #train_model()
    # draw contour on the image
    drawContour(count=5)
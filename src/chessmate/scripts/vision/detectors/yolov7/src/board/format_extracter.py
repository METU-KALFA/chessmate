import os
import json
import sys
import shutil
import numpy as np
import pybboxes as pbx

# path variables => can be handy
# DATA_PATH (string)
#   |-> relative data location from board directory
DATA_PATH = '../../data/'

# width and height of the input images
W,H = 1200,800

# piece endcoding
piece_enc = {'k':'1', 'q':'2', 'p':'3', 'b':'4', 'r':'5', 'n':'6'}

# Convert Pascal_Voc bb to Yolo
def voc_to_yolo(x1, y1, x2, y2, image_w = W, image_h = H):
    return (((x2 + x1)/(2*image_w)), ((y2 + y1)/(2*image_h)), (x2 - x1)/image_w, (y2 - y1)/image_h)

def cornersToYOLO(corners):
    xx = [corner[0] for corner in corners]
    yy = [corner[1] for corner in corners]
    [minx, maxx] = min(xx), max(xx)
    [miny, maxy] = min(yy), max(yy)
    voc_box = (minx, miny, maxx, maxy)
    return voc_to_yolo(minx, miny, maxx, maxy)

def main():
    # data-set types
    paths = ["train/", "test/", "val/"] # "train/","test/"
    for path in paths:
        # relative path to given_path
        current_path = DATA_PATH + path
        # get the list of file names in the current_path 
        files = [x[:-4] for x in os.listdir(current_path) if x.endswith('.png')]
        if not os.path.exists(f"{current_path}labels"):
            os.makedirs(f"{current_path}labels")
        if not os.path.exists(f"{current_path}images"):    
            os.makedirs(f"{current_path}images")
        for file in files:
            shutil.move(f"{current_path}{file}.png", f"{current_path}images/{file}.png")
            with open(f"{current_path}labels/{file}.txt", "w") as f:
                with open(f"{current_path}{file}.json") as j:
                    data = json.load(j)
                # chessboard
                (x,y,w,h) = cornersToYOLO(data['corners'])
                f.write(f"0 {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
                # pieces and their locations
                for piece in data['pieces']:
                    piece_class = piece_enc[piece['piece'].lower()]
                    loc = piece['box']
                    (x,y,w,h) = voc_to_yolo(loc[0], loc[1], loc[0] + loc[2], loc[1] + loc[3])
                    f.write(f"{piece_class} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


if __name__ == "__main__":
    main()

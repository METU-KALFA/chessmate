import argparse
import os
import cv2

# Crop the image for deleting the outside part of the table and optimizing the chessboard recognition
# Triggered action behaviour depends on the given arguments
#     |-> input : choose directory or a single image file
#     |-> x : amount of pixel distance to crop on x-axis
#     |-> y : amount of pixel distance to crop on y-axis 
#     |-> show : whether or not show the resulting image 
#     |-> save : whether or not save the resulting image

# types of images to do crop on
image_suffixes = ('.jpg', '.jpeg', '.png', '.svg')

def CropImage(image, x, y):
    cropped_image = image.copy()
    # Cropping on x-axis
    if(len(x) == 1):
        cropped_image = cropped_image[:,x[0]:-x[0]]
    elif(len(x) == 2):
        cropped_image = cropped_image[:,x[0]:-x[1]]

    # Cropping on y-axis
    if(len(y) == 1):
        cropped_image = cropped_image[y[0]:-y[0],:]
    elif(len(y) == 2):
        cropped_image = cropped_image[y[0]:-y[1],:]

    # return the resulting image
    return cropped_image 



if __name__ == '__main__':
    # parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='.', help='image(s) input')
    parser.add_argument('--x', nargs='+', type=int, default=[40,40], help='amount of crop on x-axis (left,right) :: if given 1 integer crop from both sides at the same amount')
    parser.add_argument('--y', nargs='+', type=int, default=[40,40], help='amount of crop on y-axis (top, bottom) :: if given 1 integer crop from both sides at the same amount')
    parser.add_argument('--show', action='store_true', help='show the resulting image(s)')
    parser.add_argument('--save', action='store_true', help='save the resulting image')
    opt = parser.parse_args()


    # Retrieve and crop the image(s)

    # get images from directory
    if(not opt.input.endswith(image_suffixes)):
        # get the images from current directory
        if(opt.input == '.'):
            fileNames = [x for x in os.listdir(opt.input) if x.endswith(image_suffixes)]
        # get images from another directory
        else:
            fileNames = [opt.input + '/' + x for x in os.listdir(opt.input) if x.endswith(image_suffixes)]
        
        # traverse and crop images on the given directory
        for name in fileNames:
            image = cv2.imread(name)
            croppedImage = CropImage(image)
            if(opt.show):
                cv2.imshow(name, croppedImage)
                cv2.waitKey(0)
            if(opt.save):
                cv2.imwrite(name, croppedImage)

    # get single image
    else:
        image = cv2.imread(opt.input)
        croppedImage = CropImage(image)
        if(opt.show):
            cv2.imshow(opt.input, croppedImage)
            cv2.waitKey(0)
        if(opt.save):
            cv2.imwrite(opt.input, croppedImage)
        

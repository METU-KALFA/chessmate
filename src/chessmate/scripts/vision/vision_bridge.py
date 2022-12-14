#!/usr/bin/env python

import rospy
import cv2
import os
from camera import Camera
from coordinate import Coordinate
from top_vision import TopVision
from side_vision import SideVision
from color_top_vision import ColorTopVision
#from face_tracer import FaceTracer
from chessmate.srv import QueryVisionComponentResponse, QueryVisionComponent, getPositionOfPieces, getPositionOfPiecesResponse 
from return_codes import *
from functools import partial
from fingerReader import fingerReader

A1_X = 0.38956775335674165
A1_Y = 0.2514168099176759
A8_X = 0.7214916931113047
A8_Y = 0.24953711004328757
H1_X = 0.393559816814854
H1_Y = -0.07928136293442133
H8_X = 0.7185953712505643
H8_Y = -0.08110556882787892






current_dir = os.path.dirname(os.path.realpath(__file__))
MISPREDICTED_IMAGE_PATH = current_dir + "/mispredicted_images/"
mispredicted_image_counter = 0
side_vision_prev_image = None


def camera_release(camera):
    camera.Stop()    



# Since the main loop is in C++, I need to make vision.py a ROS service
if __name__ == "__main__":
    print("this is vision bridge")
    coordinate_class = Coordinate(A1_X, A1_Y, A8_X, A8_Y, H1_X, H1_Y, H8_X, H8_Y)

    # init ros node8
    rospy.init_node('vision_bridge')

    def getPieceCoordinates(req):
        from_coords, to_coords = coordinate_class.get_piece_coordinates(req.from_piece, req.to_piece)
        return getPositionOfPiecesResponse(True, from_coords[0], from_coords[1], to_coords[0], to_coords[1])


    rospy.Service('/get_piece_coordinates', getPositionOfPieces, getPieceCoordinates)


    camera = Camera()
    top_vision = TopVision(camera)
    color_top = ColorTopVision(camera)
    side_vision = SideVision()
    #finger_reader = fingerReader()
    #face_tracer = FaceTracer(camera)


    def queryvisioncomponent_handler(req):
        global side_vision_prev_image
        global MISPREDICTED_IMAGE_PATH
        global mispredicted_image_counter
        #if req.query_type == "get_emotion":
        #    return_code = face_tracer.get_emotion()
        #    return QueryVisionComponentResponse(return_code,"")
            
        #if req.query_type == "align_face":
        #    return_code = face_tracer.is_face_aligned()
        #    return QueryVisionComponentResponse(return_code, "")

        if req.query_type == "test":
            return QueryVisionComponentResponse(1,"")


        if req.query_type == "read_fingers":
            image,_,_ = camera.GetImage()
            return QueryVisionComponentResponse(finger_reader.readFinger(image),"")


        if req.query_type == "update_prev":
            side_vision_prev_image,_,_ = camera.GetImage()
            return QueryVisionComponentResponse(1,"")

        if req.query_type == "side":
            current_image,_,_ = camera.GetImage()
            return_code, movement_in_fen = side_vision.get_movement(current_image,side_vision_prev_image,req.last_state_fen_string)
            if return_code == SIDE_VISION_UNSUCCESS:
                cv2.imwrite(MISPREDICTED_IMAGE_PATH + "/image-" + str(mispredicted_image_counter) + ".png", side_vision_prev_image)
                mispredicted_image_counter += 1
                cv2.imwrite(MISPREDICTED_IMAGE_PATH + "/image-" + str(mispredicted_image_counter) + ".png", current_image)
                mispredicted_image_counter += 1


        if req.query_type == "top":
            current_image,_,_ = camera.GetImage()
            return_code, movement_in_fen = top_vision.get_movement(req.last_state_fen_string)
            if return_code == TWO_DIFFERENCE_DETECTED:
                return QueryVisionComponentResponse(return_code, movement_in_fen)

            return_code, movement_in_fen = color_top.get_movement(req.last_state_fen_string)
            if return_code == TWO_DIFFERENCE_DETECTED:
                return QueryVisionComponentResponse(return_code, movement_in_fen)
            
            if return_code != TWO_DIFFERENCE_DETECTED:
                cv2.imwrite(MISPREDICTED_IMAGE_PATH + "/image-" + str(mispredicted_image_counter) + ".png", current_image)
                mispredicted_image_counter += 1


        return QueryVisionComponentResponse(return_code, movement_in_fen)



    # start a ros service
    rospy.Service('/franka_vision', QueryVisionComponent, queryvisioncomponent_handler)


    
    rospy.on_shutdown(partial(camera_release, camera))

    rospy.spin()

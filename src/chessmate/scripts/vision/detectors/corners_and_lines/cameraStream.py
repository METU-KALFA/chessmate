import pyrealsense2 as rs
import numpy as np
import cv2
import argparse
import os

# Take video or photos from Camera Stream 
#     |-> res : resolution of the image/video
#     |-> frame : frame of the video
#     |-> type : retrieve only colored(0) or color and depth together(1)


def streamer(opt):
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The script requires Depth camera with Color sensor")
        exit(0)
    
    # set arguments given by user
    frame_width, frame_height = opt.res
    fps = opt.frame
    
    if(opt.type == 1):
        config.enable_stream(rs.stream.depth, frame_width, frame_height, rs.format.z16, fps)
    config.enable_stream(rs.stream.color, frame_width, frame_height, rs.format.bgr8, fps)

    # Open windows
    cv2.namedWindow('RealSense color', cv2.WINDOW_AUTOSIZE)
    if(opt.type == 1):
        cv2.namedWindow('RealSense depth', cv2.WINDOW_AUTOSIZE)

    # Start streaming
    pipeline.start(config)
    try:
        fRecording = False
        i=0
        k=0
        while True:

            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            if(opt.type == 1):
                depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # Convert images to numpy arrays
            if(opt.type == 1):
                depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            if(opt.type == 1):
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.15), cv2.COLORMAP_JET)
                depth_colormap_dim = depth_colormap.shape

            color_colormap_dim = color_image.shape

            # If depth and color resolutions are different, resize color image to match depth image for display
            if (opt.type == 1) and (depth_colormap_dim != color_colormap_dim):
                resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))
            elif(opt.type == 1):
                images = np.hstack((color_image, depth_colormap))


            if fRecording:
                out_rgb.write(color_image)
                if(opt.type == 1):
                    out_depth.write(depth_colormap)
            
            # Show images
            cv2.imshow('RealSense color', color_image)
            if(opt.type == 1):
                cv2.imshow('RealSense depth', depth_colormap)
            
            c = cv2.waitKey(1) 
            # Toggle recording on/off
            if (c == ord('t')):
                # Start recording
                if fRecording==False: 
                    print('Recording started')
                    out_rgb = cv2.VideoWriter('output/video_'+str(k)+'.avi',cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_height))
                    if(opt.type == 1):
                        out_depth = cv2.VideoWriter('output/video_depth_'+str(k)+'.avi',cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))
                
                # Stop recording
                if fRecording==True:
                    print('Recording ended')
                    out_rgb.release()
                    if(opt.type == 1):
                        out_depth.release()
                    k=k+1
                fRecording = not fRecording
            
            # Take a photo
            elif (c == ord('s')):
                cv2.imwrite('output/frame_'+str(i)+'.jpg',color_image)
                if(opt.type == 1):
                    cv2.imwrite('output/frame_depth_'+str(i)+'.jpg',depth_colormap)
                i=i+1
            
            # Stop
            elif (c == ord('q')):
                break

    finally:
        # Stop streaming
        pipeline.stop()



if __name__ == '__main__':
    # parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--res', nargs='+', type=int, default=[1280,720], help='resoulution of the image/video stream')
    parser.add_argument('--frame', type=int, default=30, help='frame rate of the video stream')
    parser.add_argument('--type', type=int, default=0, help='stream video type color{0} or (color and depth){1}')
    opt = parser.parse_args()
    
    streamer(opt)
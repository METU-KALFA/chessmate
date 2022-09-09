import pyrealsense2 as rs
import numpy as np
import cv2

pipeline = rs.pipeline()
config = rs.config()

# colorizer = rs.colorizer()
align = rs.align(rs.stream.depth)

align_stream = rs.align(rs.stream.color)

config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16,30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
pipeline.start(config)



try:
    while True:

        frameset = pipeline.wait_for_frames()

        matched_frames = align.process(frameset)

        aligned_frames = align_stream.process(frameset)

        matched_frame = matched_frames.get_color_frame()
        # depth_frame2 = matched_frames.get_depth_frame()

        aligned_color_frame = aligned_frames.get_color_frame()
        aligned_depth_frame = aligned_frames.get_depth_frame()

        matched_image = np.asanyarray(matched_frame.get_data())
        # depth_image2 = np.asanyarray(depth_frame2.get_data())

        aligned_color_image = np.asanyarray(aligned_color_frame.get_data())
        aligned_depth_image = np.asanyarray(aligned_depth_frame.get_data())

        # Show images
        cv2.imshow('RealSenseDepthC', matched_image)
        # cv2.imshow('RealSenseDepthD', depth_image2)

        cv2.imshow('RealSenseDepthColor', aligned_color_image)
        cv2.imshow('RealSenseDepth', aligned_depth_image)  

        cv2.waitKey(1)


finally:

    # Stop streaming
    pipeline.stop()
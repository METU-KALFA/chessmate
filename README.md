# ChessMate
<hr>
## Control

First, make sure that franka_ros and moveit packages are sourced. Connect chesswatch and RealSense camera to the computer with usb. Make sure that camera is connected to a usb 3.2 port. The system requires stockfish engine. Its path must be specified in src/chessmate/scripts/vision/top_vision.py as STOCKFISH_PATH variable. Then run ./bash/launch_all.sh to start the system. This should open several chessmate nodes as different terminal tabs. Some of these tabs may immediately crash when a required software or hardware connection is missing. If the system is not working and you can not see any errors, it may be due to that.

Through summer internship period, move_piece node is added to the system. This node provides "move_piece" service that allows movement of pieces between grids specified in a form like "{move_from="a4", move_to="a2"}". Also it provides "set_chessboard_position" service to get the position of the chessboard. Ideally, vision part of the system should determine the coordinates of the corners as 3D camera coordinates using depth camera, convert these coordinates to the robot's coordinate system and use this service to transmit the x and y coordinates of these four points to the move_piece node. However coordinate conversion is not implemented and corner detection is not integrated to ChessMate yet.

TODO: Add Claudio's vision code to the src/chessmate/scripts/vision.

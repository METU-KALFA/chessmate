# ChessMate
<hr>

## Control

### Pre-requirements

- First, make sure that franka_ros and moveit packages are sourced. 
- Connect chesswatch and RealSense camera to the computer with usb. 
- Make sure that camera is connected to a usb 3.2 port. 
- The system requires stockfish engine. Its path must be specified in src/chessmate/scripts/vision/top_vision.py as STOCKFISH_PATH variable. 
- Then run ./bash/launch_all.sh to start the system. This should open several chessmate nodes as different terminal tabs. Some of these tabs may immediately crash when a required software or hardware connection is missing. If the system is not working and you can not see any errors, it may be due to that.

<br>

### Changes

- Through summer internship period, move_piece node is added to the system. This node provides "move_piece" service that allows movement of pieces between grids specified in a form like "{move_from="a4", move_to="a2"}". Also it provides "set_chessboard_position" service to get the position of the chessboard.
- Ideally, vision part of the system should determine the coordinates of the corners as 3D camera coordinates using depth camera, convert these coordinates to the robot's coordinate system and use this service to transmit the x and y coordinates of these four points to the move_piece node. However coordinate conversion is not implemented and corner detection is not integrated to ChessMate yet.


<hr>

## Vision



<br>

### Corners and Lines

- This part can detect the corners of the chessboard with usually more than 0.80 confidence.
- After detecting the corners, Projective Transformation applied and the focusing area is shrinked down to only chessboard and a little frame around it.
- After the focus, algorithm then tries to detect the squares on chessboard. At that point, squares are feed into a validation to have much more precise borders.
- Algorithm can also extract the squares and the pieces over them individually.


### YOLO
  - YOLOV7 pre-trained model trained over a large syntetic dataset. 
  - Even though the obtained model can perform with significant success on real-world data, we wanted study further.
  - By using the _cameraStream.py_ we recorded some videos from a variety of schenes with different chess piece locations, and extracted frames out of the videos and filtered only the good quality, non-blurred and fully visible chessboard images.
  - Then we trained the already obtained model on real-world data and get better results on rook and bishop. However, model cannot distinguish between queens from bishops or knights from pawns most of the time. This part needs further studies and collection of more data to train with. 

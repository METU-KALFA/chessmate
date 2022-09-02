#include <ros/ros.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit/move_group_interface/move_group_interface.h>
#include <chessmate/chessboard_position.h>
#include <chessmate/move_piece.h>
#include <franka_gripper/GripperCommand.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>

typedef struct point {
	double x;
	double y;
} point;

// The circle constant tau = 2*pi. One tau is one rotation in radians.
const double tau = 2 * M_PI;

// Table and chessboard objects
std::vector<moveit_msgs::CollisionObject> collision_objects;

// Interfaces defined as pointers to allow access from callback functions
moveit::planning_interface::PlanningSceneInterface * planning_scene_interface;
moveit::planning_interface::MoveGroupInterface * move_group_interface;

// Approximate coordinates of marked points on the table. (border widths subtracted)
point chessboard_corners[4] = {{0.3780, -0.1068}, {0.3780, 0.272}, {0.754, 0.272}, {0.754, -0.1068}};

/*
chessboard_corners[2]	------------------------- chessboard_corners[3]
                        |8 |  |  |  |  |  |  |  |
                        -------------------------
                        |7 |  |  |  |  |  |  |  |
                        -------------------------
                        |6 |  |  |  |  |  |  |  |
                        -------------------------
                        |5 |  |  |  |  |  |  |  | 
                        ------------------------- 
                        |4 |  |  |  |  |  |  |  |
                        -------------------------
                        |3 |  |  |  |  |  |  |  |
                        -------------------------
                        |2 |  |  |  |  |  |  |  |
                        -------------------------
                        |1a| b| c| d| e| f| g| h|
chessboard_corners[1]   ------------------------- chessboard_corners[0]
                                ||ROBOT||
*/

// Coordinates of the center of the requested grid.
point target;

//double border_width[4] = {0.01, 0.01, 0.01, 0.01}; SHOULD BE CONSIDERED WHEN CALCULATING CHESSBOARD CORNERS

point chess_to_coor (std::string position)
{
	point result = {0, 0};
	int x = 2 * (position[0] - 'a') + 1; // j for out
	int y = 2 * (position[1] - '1') + 1; // 4 for out

	if (x < 1 || x > 19 || y < 1 || y > 15) { 
		ROS_ERROR_STREAM("Invalid Chess Grid, returning a1");
		x = 1;
		y = 1;
	}

	// Calculate center coordinates of the grid
	result.x = (chessboard_corners[1].x * (16-y) + chessboard_corners[2].x * y) / 16;
	result.x += (chessboard_corners[1].x * (16-x) + chessboard_corners[0].x * x) / 16 - chessboard_corners[1].x;

	result.y = (chessboard_corners[1].y * (16-y) + chessboard_corners[2].y * y) / 16;
	result.y += (chessboard_corners[1].y * (16-x) + chessboard_corners[0].y * x) / 16 - chessboard_corners[1].y;

	return result;
}

void pick (moveit::planning_interface::MoveGroupInterface* move_group_interface, ros::ServiceClient gripper_client)
{
	franka_gripper::GripperCommand gripper_request;
	geometry_msgs::Pose target_pose;
	tf2::Quaternion orientation;
	orientation.setRPY(tau/2, 0, -tau/8);
	gripper_request.request.speed = 0.05;
	gripper_request.request.force = 20;
	gripper_request.request.want_to_pick = false;
	gripper_request.request.want_to_move = true;
	gripper_request.request.homing = false;

	ROS_INFO_STREAM("PICKING");

	// Open gripper
	gripper_request.request.want_to_pick = false;
	gripper_request.request.width = 0.035;
	gripper_client.call(gripper_request);

	target_pose.orientation = tf2::toMsg(orientation);
	target_pose.position.x = target.x;
	target_pose.position.y = target.y;

	// Move down
	target_pose.position.z = 0.305;
	move_group_interface->setPoseTarget(target_pose);
	move_group_interface->move();

	// Close gripper
	gripper_request.request.want_to_pick = true;
	gripper_request.request.width = 0.01;
	gripper_client.call(gripper_request);

	// Move up
	target_pose.position.z = 0.4;
	move_group_interface->setPoseTarget(target_pose);
	move_group_interface->move();
}

void place (moveit::planning_interface::MoveGroupInterface* move_group_interface, ros::ServiceClient gripper_client)
{
	franka_gripper::GripperCommand gripper_request;
	geometry_msgs::Pose target_pose;
	tf2::Quaternion orientation;
	orientation.setRPY(tau/2, 0, -tau/8);
	gripper_request.request.speed = 0.05;
	gripper_request.request.force = 20;
	gripper_request.request.want_to_pick = false;
	gripper_request.request.want_to_move = true;
	gripper_request.request.homing = false;

	ROS_INFO_STREAM("PLACING");
	
	target_pose.orientation = tf2::toMsg(orientation);
	target_pose.position.x = target.x;
	target_pose.position.y = target.y;

	// Move down
	target_pose.position.z = 0.305;
	move_group_interface->setPoseTarget(target_pose);
	move_group_interface->move();

	// Open gripper;
	gripper_request.request.width = 0.035;
	gripper_client.call(gripper_request);

	// Move up
	target_pose.position.z = 0.4;
	move_group_interface->setPoseTarget(target_pose);
	move_group_interface->move();
}

void setCollisionObjects (moveit::planning_interface::PlanningSceneInterface* planning_scene_interface)
{
	// Table
	// Add the table.
	collision_objects[0].header.frame_id = "panda_link0";
	collision_objects[0].id = "table";

	// Define the primitive and its dimensions.
	collision_objects[0].primitives.resize(1);
	collision_objects[0].primitives[0].type = collision_objects[0].primitives[0].BOX;
	collision_objects[0].primitives[0].dimensions.resize(3);
	collision_objects[0].primitives[0].dimensions[0] = 1;
	collision_objects[0].primitives[0].dimensions[1] = 1;
	collision_objects[0].primitives[0].dimensions[2] = 0.12;

	// Define the pose of the table.
	collision_objects[0].primitive_poses.resize(1);
	collision_objects[0].primitive_poses[0].position.x = 0.65;
	collision_objects[0].primitive_poses[0].position.y = 0;
	collision_objects[0].primitive_poses[0].position.z = 0.06;
	collision_objects[0].primitive_poses[0].orientation.w = 1.0;

	collision_objects[0].operation = collision_objects[0].ADD;

	// Chessboard
	// Define the board.
	collision_objects[1].header.frame_id = "panda_link0";
	collision_objects[1].id = "board";

	// Define the primitive and its dimensions.
	collision_objects[1].primitives.resize(1);
	collision_objects[1].primitives[0].type = collision_objects[1].primitives[0].BOX;
	collision_objects[1].primitives[0].dimensions.resize(3);
	collision_objects[1].primitives[0].dimensions[0] = abs(chessboard_corners[0].x - chessboard_corners[2].x); //0.35
	collision_objects[1].primitives[0].dimensions[1] = abs(chessboard_corners[0].y - chessboard_corners[1].y); //0.35
	collision_objects[1].primitives[0].dimensions[2] = 0.1;

	// Define the pose of the object.
	collision_objects[1].primitive_poses.resize(1);
	collision_objects[1].primitive_poses[0].position.x = (chessboard_corners[0].x + chessboard_corners[1].x + chessboard_corners[2].x + chessboard_corners[3].x) / 4; //0.6
	collision_objects[1].primitive_poses[0].position.y = (chessboard_corners[0].y + chessboard_corners[1].y + chessboard_corners[2].y + chessboard_corners[3].y) / 4;   //0
	collision_objects[1].primitive_poses[0].position.z = 0.17;
	collision_objects[1].primitive_poses[0].orientation.w = 1.0;

	collision_objects[1].operation = collision_objects[1].ADD;

	planning_scene_interface->applyCollisionObjects(collision_objects);
}

void hideBoard (moveit::planning_interface::PlanningSceneInterface* planning_scene_interface)
{
	collision_objects[1].operation = collision_objects[1].REMOVE;
	planning_scene_interface->applyCollisionObjects(collision_objects);
}

void restoreBoard (moveit::planning_interface::PlanningSceneInterface* planning_scene_interface)
{
	collision_objects[1].operation = collision_objects[1].ADD;

	planning_scene_interface->applyCollisionObjects(collision_objects);
}

void move_above (moveit::planning_interface::MoveGroupInterface* move_group_interface, std::string target_str)
{
	target = chess_to_coor(target_str);

	ROS_INFO_STREAM("X: " << target.x);
	ROS_INFO_STREAM("Y: " << target.y);

	geometry_msgs::Pose target_pose;
	geometry_msgs::Pose start_pose = move_group_interface->getCurrentPose().pose;
	tf2::Quaternion orientation;
	moveit_msgs::OrientationConstraint ocm;
	moveit_msgs::Constraints test_constraints;

	// Orientation constraints are added to avoid excessive movements of some of the joints.
	// Values used in ocm are emprically determined and most probably unoptimal. Better constraints
	// are needed to be set to make robot movement look more natural.
	ocm.link_name = "panda_link1";
	ocm.header.frame_id = "panda_link0";
	ocm.orientation.w = 1.5;
	ocm.absolute_x_axis_tolerance = 1.5;
	ocm.absolute_y_axis_tolerance = 1.5;
	ocm.absolute_z_axis_tolerance = 1.5;
	ocm.weight = 1.0;
	test_constraints.orientation_constraints.push_back(ocm);
	ocm.link_name = "panda_link3";
	test_constraints.orientation_constraints.push_back(ocm);
	move_group_interface->setPathConstraints(test_constraints);

	// Goal orientation set as roll, pitch, yawn angles.
	orientation.setRPY(tau/2, 0, -tau/8);
	target_pose.orientation = tf2::toMsg(orientation);
	target_pose.position.x = target.x;
	target_pose.position.y = target.y;
	target_pose.position.z = 0.4;
	move_group_interface->setPoseTarget(target_pose);
	move_group_interface->move();

	move_group_interface->clearPathConstraints();
}

bool set_chessboard_position (chessmate::chessboard_position::Request &req, chessmate::chessboard_position::Response &resp)
{
	ROS_INFO_STREAM("Chessboard position set.");

	chessboard_corners[0].x = req.corner_0[0];
	chessboard_corners[0].y = req.corner_0[1];

	chessboard_corners[1].x = req.corner_1[0];
	chessboard_corners[1].y = req.corner_1[1];
	
	chessboard_corners[2].x = req.corner_2[0];
	chessboard_corners[2].y = req.corner_2[1];

	chessboard_corners[3].x = req.corner_3[0];
	chessboard_corners[3].y = req.corner_3[1];

	setCollisionObjects(planning_scene_interface);

	return true;
}

bool move_piece (chessmate::move_piece::Request &req, chessmate::move_piece::Response &resp, ros::NodeHandle nh)
{
	ros::ServiceClient gripper_client = nh.serviceClient<franka_gripper::GripperCommand>("/franka_custom_gripper_service");

	ROS_INFO_STREAM("Moving from: " << req.move_from << " to: " << req.move_to);
	
	// hideBoard & restoreBoard are disabled since they may be unnecessary.
	move_above(move_group_interface, req.move_from);
	//hideBoard(planning_scene_interface);
	pick(move_group_interface, gripper_client);
	//restoreBoard(planning_scene_interface);
	move_above(move_group_interface, req.move_to);
	//hideBoard(planning_scene_interface);
	place(move_group_interface, gripper_client);
	//restoreBoard(planning_scene_interface);
	resp.return_code = 0;
	return true;
}

int main (int argc, char** argv)
{
	ros::init(argc, argv, "move_piece");
	ros::NodeHandle nh;
	ros::AsyncSpinner spinner(2);
	spinner.start();
	planning_scene_interface = new moveit::planning_interface::PlanningSceneInterface();
	move_group_interface = new moveit::planning_interface::MoveGroupInterface("panda_arm");

	move_group_interface->setPlanningTime(45.0);
	move_group_interface->setMaxVelocityScalingFactor(0.3);
	move_group_interface->setMaxAccelerationScalingFactor(0.15);

	collision_objects.resize(2);
	setCollisionObjects(planning_scene_interface);
	hideBoard(planning_scene_interface);

	// Service to set position of the chessboard
	ros::ServiceServer set_server = nh.advertiseService("set_chessboard_position", &set_chessboard_position);

	// Service to move pieces
	ros::ServiceServer move_server = nh.advertiseService<chessmate::move_piece::Request, chessmate::move_piece::Response>("move_piece", boost::bind(&move_piece, _1, _2, boost::ref(nh)));

	ros::waitForShutdown();
	return 0;
}

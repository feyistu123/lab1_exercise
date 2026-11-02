# Lab 1 Exercise: Program diffdrive_bot

**Student:** Feyistu Endale
**Course:** Introduction to Robotics and Intelligent Systems

## How to Build
To build the packages, place the `lab1_exercise` folder inside the `src` directory of your ROS 2 workspace (e.g., `~/ros2_ws/src`), then run:
```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash

How to Run Each Step
Step 1 (Sensors):
To view the robot model and the new depth camera/IMU in RViz:

bash
ros2 launch diffdrive_bot display.launch.py
To run the simulation in Gazebo:

bash
ros2 launch diffdrive_bot gazebo.launch.py
Steps 2-5 (Turn Away, Parameters, Custom Msg, Services):

bash
ros2 run my_robot_nodes turn_away
Step 6 (Rotate Action Server):

bash
ros2 run my_robot_nodes rotate_server
Step 7 (Square Driver & Launch File):

bash
ros2 launch my_robot_nodes square.launch.py side_length:=0.8

What did not work and why?
VirtualBox Odometry Lag: Because I am running Ubuntu and Gazebo inside a VirtualBox Virtual Machine, the 3D graphics acceleration is disabled. This causes the Gazebo physics engine to run extremely slowly. As a result, the /odom (odometry) topic drops messages and does not update in real-time.

To handle this, I added a "safety timeout" to the rotate_server and drive_distance_server nodes. This prevents the robot from spinning or driving infinitely if the odometry fails to update. On a native machine with proper graphics acceleration, the odometry works perfectly, the timeouts are never triggered, and the robot drives a perfect square.
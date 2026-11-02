import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Declare the side_length argument
    side_length_arg = DeclareLaunchArgument(
        'side_length', default_value='0.5',
        description='Length of the square sides in meters'
    )
    
    side_length = LaunchConfiguration('side_length')

    # 2. Include the robot's control.launch.py (starts Gazebo, RViz, etc.)
    diffdrive_bot_dir = get_package_share_directory('diffdrive_bot')
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(diffdrive_bot_dir, 'launch', 'control.launch.py')
        )
    )

    # 3. Start the drive_distance_server (the action server to drive forward)
    drive_server = Node(
        package='my_robot_nodes',
        executable='drive_distance_server',
        name='drive_distance_server',
        output='screen'
    )

    # 4. Start the rotate_server (the action server to turn)
    rotate_server = Node(
        package='my_robot_nodes',
        executable='rotate_server',
        name='rotate_server',
        output='screen'
    )

    # 5. Start the square_driver (the client that drives the square)
    square_driver = Node(
        package='my_robot_nodes',
        executable='square_driver',
        name='square_driver',
        parameters=[{'side_length': side_length}],
        output='screen'
    )

    return LaunchDescription([
        side_length_arg,
        control_launch,
        drive_server,
        rotate_server,
        square_driver
    ])

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    use_gui = LaunchConfiguration('gui')
    mode = LaunchConfiguration('mode')   #NEW

    robot_description = ParameterValue(
        Command([
            'xacro ',
            PathJoinSubstitution([
                FindPackageShare('assem2_description'),
                'urdf',
                'assem2.urdf'
            ])
        ]),
        value_type=str
    )

    return LaunchDescription([

        # -----------------------------
        # LAUNCH ARGUMENTS
        # -----------------------------
        DeclareLaunchArgument(
            'gui',
            default_value='true',
            description='Use joint_state_publisher_gui'
        ),

        DeclareLaunchArgument(
            'mode',
            default_value='five',
            description='Hand control mode: three | four | five'
        ),

        # -----------------------------
        # NODES
        # -----------------------------
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),

        Node(
            package='hand_controller',
            executable='hand_joint_publisher',
            output='screen',
            parameters=[{'mode': mode}]   # PASS PARAM HERE
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            condition=UnlessCondition(use_gui)
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            output='screen'
        )
    ])



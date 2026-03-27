import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    lar_share = get_package_share_directory('lar_gazebo')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    clearpath_gz_share = get_package_share_directory('clearpath_gz')

    world_file = os.path.join(lar_share, 'worlds', 'lar.world')
    models_dir = os.path.join(lar_share, 'models')
    worlds_dir = os.path.join(lar_share, 'worlds')

    setup_path = LaunchConfiguration('setup_path')
    world_name = LaunchConfiguration('world_name')
    rviz = LaunchConfiguration('rviz')
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    yaw = LaunchConfiguration('yaw')

    existing_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    combined_resource_path = ':'.join(
        p for p in [models_dir, worlds_dir, lar_share, existing_resource_path] if p
    )

    gz_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r -v 4 {world_file}'
        }.items()
    )

    husky_spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(clearpath_gz_share, 'launch', 'robot_spawn.launch.py')
        ),
        launch_arguments={
            'setup_path': setup_path,
            'world': world_name,
            'rviz': rviz,
            'use_sim_time': 'true',
            'generate': 'true',
            'x': x,
            'y': y,
            'z': z,
            'yaw': yaw,
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'setup_path',
            default_value=os.path.join(os.environ['HOME'], 'clearpath'),
            description='Path that contains robot.yaml'
        ),
        DeclareLaunchArgument(
            'world_name',
            default_value='default',
            description='Must match <world name=\"...\"> inside lar.world'
        ),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('z', default_value='0.3'),
        DeclareLaunchArgument('yaw', default_value='0.0'),

        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', combined_resource_path),

        gz_world,
        husky_spawn,
    ])

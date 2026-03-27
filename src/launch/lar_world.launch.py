import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_share = get_package_share_directory('lar_gazebo')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    world = LaunchConfiguration('world')
    verbose = LaunchConfiguration('verbose')

    default_world = os.path.join(pkg_share, 'worlds', 'lar.world')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r -v ', verbose, ' ', world],
            'on_exit_shutdown': 'true',
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Full path to world file'
        ),
        DeclareLaunchArgument(
            'verbose',
            default_value='4',
            description='Gazebo verbosity level'
        ),

        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(pkg_share, 'models')
        ),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(pkg_share, 'worlds')
        ),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            pkg_share
        ),

        gz_sim,
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    AppendEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def _flag(config_name, flag, when='false'):
    """Emit ``flag`` (plus a trailing space) only when ``config_name`` == ``when``.

    Used to splice optional ``gz sim`` switches into the gz_args string, which
    has to stay a substitution list -- launch arguments are not resolved at
    generate_launch_description() time.
    """
    return PythonExpression([
        "'", flag, " ' if '", LaunchConfiguration(config_name), "' == '", when, "' else ''",
    ])


def generate_launch_description():
    """Bring up the LAR world + Clearpath a200 (Husky) in Gazebo (gz/Jazzy).

    Clearpath's bundled ``simulation.launch.py`` restricts ``world`` to a fixed
    list of its own worlds (warehouse/office/...), so it cannot load the custom
    LAR world. Instead we:

      1. start Gazebo with the generic ``ros_gz_sim`` launch pointed straight at
         ``worlds/lar.world`` (same proven approach as ``lar_world.launch.py``,
         which also resolves the LAR furniture/tag models);
      2. bridge ``/clock`` (Clearpath's gz_sim normally does this for us);
      3. spawn the robot + sensor/platform bridges via Clearpath's
         ``robot_spawn.launch.py``.

    ``world`` passed to robot_spawn must be the *internal* world name (the
    ``<world name="...">`` inside lar.world, which is ``default``) because it
    only feeds the gz->ROS bridge topic prefix ``/world/<name>/model/...``.
    """
    pkg_clearpath_gz = get_package_share_directory("clearpath_gz")
    pkg_lar_gazebo = get_package_share_directory("lar_gazebo")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")

    # The <world name="..."> inside lar.world. Drives the bridge topic prefix.
    world_name = "default"

    setup_path_arg = DeclareLaunchArgument(
        "setup_path",
        default_value=os.path.join(pkg_lar_gazebo, "config"),
        description="Path to clearpath configuration (robot.yaml)",
    )
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) clock",
    )
    gui_arg = DeclareLaunchArgument(
        "gui",
        default_value="true",
        description="Show the Gazebo GUI. false runs the server only (gz sim -s); "
                    "physics and sensors still run, so Unity keeps getting data.",
    )
    headless_rendering_arg = DeclareLaunchArgument(
        "headless_rendering",
        default_value="false",
        description="Render the camera/LiDAR sensors through EGL instead of a "
                    "display (gz sim --headless-rendering). Needed with gui:=false "
                    "over SSH or on a machine with no X session.",
    )

    models_path = os.path.join(pkg_lar_gazebo, "models")
    worlds_path = os.path.join(pkg_lar_gazebo, "worlds")
    world_file = os.path.join(worlds_path, "lar.world")

    # Gazebo resolves package:// mesh URIs (the a200 meshes) and model:// LAR
    # props by searching GZ_SIM_RESOURCE_PATH. The generic ros_gz_sim launch does
    # not set it up the way Clearpath's does, so add the LAR dirs plus every
    # sourced package's share/ dir (this is what Clearpath's gz_sim does too).
    ament_shares = ":".join(
        os.path.join(p, "share")
        for p in os.environ.get("AMENT_PREFIX_PATH", "").split(":")
        if p
    )

    # 1. Gazebo + the LAR world.
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": [
                "-r -v 4 ",
                _flag("gui", "-s", when="false"),
                _flag("headless_rendering", "--headless-rendering", when="true"),
                world_file,
            ],
            "on_exit_shutdown": "true",
        }.items(),
    )

    # 2. /clock bridge (sim time source for everything downstream).
    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        output="screen",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
    )

    # 3. Spawn the a200 + its sensor/platform bridges.
    robot_spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_clearpath_gz, "launch", "robot_spawn.launch.py")
        ),
        launch_arguments={
            "setup_path": LaunchConfiguration("setup_path"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "world": world_name,
        }.items(),
    )

    return LaunchDescription(
        [
            setup_path_arg,
            use_sim_time_arg,
            gui_arg,
            headless_rendering_arg,
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", models_path),
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", worlds_path),
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", pkg_lar_gazebo),
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", ament_shares),
            gz_sim,
            clock_bridge,
            robot_spawn,
        ]
    )

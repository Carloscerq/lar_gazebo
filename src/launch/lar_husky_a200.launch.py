import os
import re

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    AppendEnvironmentVariable,
    OpaqueFunction,
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


# Worlds that can be named directly with world:=<key>. Anything else is taken
# as a path to a world file.
_WORLDS = {
    'lar': ('lar_gazebo', 'worlds/lar.world'),
    'warehouse': ('clearpath_gz', 'worlds/warehouse.sdf'),
    'office': ('clearpath_gz', 'worlds/office.sdf'),
    'construction': ('clearpath_gz', 'worlds/construction.sdf'),
    'orchard': ('clearpath_gz', 'worlds/orchard.sdf'),
    'pipeline': ('clearpath_gz', 'worlds/pipeline.sdf'),
    'solar_farm': ('clearpath_gz', 'worlds/solar_farm.sdf'),
}


def _resolve_world(key):
    """Map a world:= value to (file path, internal <world name>).

    The internal name matters and is not cosmetic: it becomes the gz->ROS
    bridge topic prefix (/world/<name>/model/...), so hardcoding it -- as this
    launch used to, with 'default' -- silently breaks every bridged topic the
    moment a different world is loaded. lar.world happens to be named 'default'
    while Clearpath's warehouse.sdf is named 'warehouse'. Read it back out of
    the file instead of trying to keep a table in sync.
    """
    if key in _WORLDS:
        package, relative = _WORLDS[key]
        path = os.path.join(get_package_share_directory(package), relative)
    else:
        path = key

    if not os.path.isfile(path):
        raise RuntimeError(
            f'World {key!r} resolved to {path!r}, which does not exist. '
            f'Use one of {sorted(_WORLDS)} or pass a path to a world file.'
        )

    match = re.search(r'<world\s+name=[\'"]([^\'"]+)[\'"]', open(path).read())
    if not match:
        raise RuntimeError(f'No <world name="..."> found in {path!r}.')

    return path, match.group(1)


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
    ``<world name="...">`` inside the world file) because it only feeds the
    gz->ROS bridge topic prefix ``/world/<name>/model/...``. That name is read
    back out of the chosen world file rather than hardcoded -- see
    ``_resolve_world``.

    Flags:
      world:=warehouse           Clearpath's warehouse (default)
      world:=lar                 the LAR lab world
      world:=/path/to/x.sdf      any world file
      gui:=false                 no Gazebo window (server only)
      headless_rendering:=true   render sensors via EGL (no X session at all)
      x:= y:= z:= yaw:=          robot spawn pose
    """
    pkg_lar_gazebo = get_package_share_directory("lar_gazebo")

    world_arg = DeclareLaunchArgument(
        "world",
        default_value="warehouse",
        description="World to load: one of "
                    f"{sorted(_WORLDS)}, or a path to a world file.",
    )
    spawn_pose_args = [
        DeclareLaunchArgument(
            name, default_value=default,
            description=f"Robot spawn {name}.",
        )
        for name, default in (("x", "0.0"), ("y", "0.0"), ("z", "0.15"), ("yaw", "0.0"))
    ]

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

    # Gazebo resolves package:// mesh URIs (the a200 meshes, the AprilTag
    # texture) and model:// LAR props by searching GZ_SIM_RESOURCE_PATH. The
    # generic ros_gz_sim launch does not set it up the way Clearpath's does, so
    # add the LAR dirs plus every sourced package's share/ dir (this is what
    # Clearpath's gz_sim does too).
    ament_shares = ":".join(
        os.path.join(p, "share")
        for p in os.environ.get("AMENT_PREFIX_PATH", "").split(":")
        if p
    )

    # 2. /clock bridge (sim time source for everything downstream).
    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        output="screen",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
    )

    return LaunchDescription(
        [
            world_arg,
            *spawn_pose_args,
            setup_path_arg,
            use_sim_time_arg,
            gui_arg,
            headless_rendering_arg,
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", models_path),
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", worlds_path),
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", pkg_lar_gazebo),
            AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", ament_shares),
            clock_bridge,
            # Gazebo and robot_spawn both need the world resolved first, which
            # cannot happen until launch arguments exist -- hence OpaqueFunction.
            OpaqueFunction(function=_launch_world_and_robot),
        ]
    )


def _launch_world_and_robot(context, *args, **kwargs):
    """Start Gazebo on the requested world, then spawn the robot into it."""
    pkg_clearpath_gz = get_package_share_directory("clearpath_gz")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")

    world_file, world_name = _resolve_world(
        LaunchConfiguration("world").perform(context)
    )

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

    robot_spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_clearpath_gz, "launch", "robot_spawn.launch.py")
        ),
        launch_arguments={
            "setup_path": LaunchConfiguration("setup_path"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "world": world_name,
            "x": LaunchConfiguration("x"),
            "y": LaunchConfiguration("y"),
            "z": LaunchConfiguration("z"),
            "yaw": LaunchConfiguration("yaw"),
        }.items(),
    )

    return [gz_sim, robot_spawn]

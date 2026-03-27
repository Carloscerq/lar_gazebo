# WIP - ROS2 lar_gazebo

ROS 2 / Gazebo Sim port of the LAR / UFBA laboratory environment.

> **Recommended branch name:** `rolling-devel`  
> **Main target stack of this branch:** **ROS 2 Rolling** + **Gazebo Jetty** + **Ubuntu 24.04**

This branch contains a ROS 2 / Gazebo Sim adaptation of the original `lar_gazebo` package, which was created for ROS 1 and Gazebo Classic.

## What this branch provides

- the **LAR laboratory world**
- the **environment models**
- ROS 2 launch files for loading the world in Gazebo Sim
- compatibility fixes for Gazebo Jetty
- a practical path to integrate the **official Clearpath Husky A200 ROS 2 stack** into the laboratory environment

---

## 1. Scope of this branch

The original repository was designed for **ROS 1** and **Gazebo Classic**. This branch adapts it to:

- **ROS 2 Rolling**
- **Gazebo Jetty**
- `ament_cmake`
- `ros_gz_sim`

This branch focuses on the **environment side** of the migration: world loading, models, launch files, resource paths, and Gazebo Sim compatibility.

---

## 2. Current status

This branch includes:

- migration from **catkin** to **ament_cmake**
- migration from ROS 1 XML launch files to **ROS 2 Python launch files**
- world loading through **`ros_gz_sim`**
- resource resolution through **`GZ_SIM_RESOURCE_PATH`**
- cleanup of legacy Gazebo Classic constructs from the world file
- model updates to improve runtime stability in Gazebo Jetty

### Important notes

Some models originally created for Gazebo Classic may need adjustments when used in Gazebo Sim. In practice, the main issues are usually:

- custom **Ogre material scripts** no longer behaving as in Gazebo Classic
- mesh-based collisions that are fragile or unstable in Gazebo Sim
- texture scaling tricks that depended on old Ogre script features

For those cases, the most reliable fixes are usually:

- replacing custom material scripts with supported SDF / PBR material definitions
- simplifying collision geometry
- using mesh UVs instead of legacy material-script texture scaling

---

## 3. Repository layout

Depending on how the migration is organized locally, the package may keep resources under `src/`.

Typical structure used in this branch:

```text
lar_gazebo/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── lar_world.launch.py
│   └── lar_husky_a200.launch.py   # optional integration wrapper
├── src/
│   ├── worlds/
│   │   └── lar.world
│   ├── models/
│   │   └── ...
│   └── maps/
│       └── ...
└── README.md
```

---

## 4. Requirements for the `rolling-devel` branch

### Operating system

- **Ubuntu 24.04**

### ROS / Gazebo stack

- **ROS 2 Rolling**
- **Gazebo Jetty**
- `ros_gz_sim`

### Notes

Gazebo Jetty binaries are provided for Ubuntu 24.04, and Gazebo's ROS installation guide explains that non-default ROS / Gazebo combinations may require extra care, especially when using packages from `packages.osrfoundation.org` or building parts from source.

---

## 5. Installing `lar_gazebo` in ROS 2 Rolling + Gazebo Jetty

### 5.1 Create the workspace

```bash
mkdir -p ~/lar_gazebo_ws/src
cd ~/lar_gazebo_ws/src
```

### 5.2 Clone the repository and switch to `rolling-devel`

```bash
git clone https://github.com/lar-deeufba/lar_gazebo.git
cd lar_gazebo
git switch rolling-devel
```

If the branch does not exist locally yet:

```bash
git switch -c rolling-devel
```

### 5.3 Source ROS 2 Rolling

```bash
source /opt/ros/rolling/setup.bash
```

### 5.4 Install dependencies

```bash
cd ~/lar_gazebo_ws
rosdep install --from-paths src --ignore-src -r -y
```

### 5.5 Build

```bash
colcon build --symlink-install
```

### 5.6 Source the workspace

```bash
source ~/lar_gazebo_ws/install/setup.bash
```

---

## 6. Running the LAR laboratory world

Launch the laboratory world with:

```bash
ros2 launch lar_gazebo lar_world.launch.py
```

This branch uses `ros_gz_sim` to launch Gazebo Sim from ROS 2.

---

## 7. Resource-path notes

The launch file should configure `GZ_SIM_RESOURCE_PATH` so Gazebo can find:

- local models
- local world files
- textures and materials

If Gazebo opens but some models are missing, black, or unresolved, the first thing to check is whether `GZ_SIM_RESOURCE_PATH` contains the package `models/` and `worlds/` directories.

---

## 8. Official Clearpath Husky A200 installation (recommended path)

If you want to use the **official Clearpath Husky A200 ROS 2 stack**, the most reliable approach is to install it in a **separate supported workspace/environment**, validate it there, and only then integrate it with `lar_gazebo`.

### Why a separate workspace?

This repository targets **Rolling + Jetty**, while the current Clearpath documentation is centered on **ROS 2 Jazzy**, the Clearpath configuration system, and the Clearpath simulator workflow.

For the Husky A200, the recommended path is therefore:

- validate the robot first using the **official Clearpath stack**
- then integrate that validated robot into the laboratory world

---

## 9. Installing the official Husky A200 simulator stack

### 9.1 Prepare a separate setup directory

The Clearpath workflow uses a setup directory such as `~/clearpath` containing `robot.yaml` and generated files.

```bash
mkdir -p ~/clearpath
```

### 9.2 Install Clearpath packages

In the official Clearpath workflow, the simulator installation is based on the offboard-computer setup and the simulator package.

```bash
sudo apt-get update
sudo apt-get install ros-jazzy-clearpath-desktop
sudo apt-get install ros-jazzy-clearpath-simulator
```

### 9.3 Create `robot.yaml`

Place your Husky A200 configuration in:

```text
~/clearpath/robot.yaml
```

A minimal example structure is:

```yaml
serial_number: a200-0000
version: 0

system:
  username: administrator
  hosts:
    - hostname: cpr-a200-0000
      ip: 192.168.131.1
  ros2:
    namespace: a200_0000
    domain_id: 0
    middleware:
      implementation: rmw_fastrtps_cpp
    workspaces: []

platform:
  controller: ps4
  battery:
    model: ES20_12C
    configuration: S2P1
  attachments:
    - name: front_bumper
      type: a200.bumper
      model: default
      parent: front_bumper_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      enabled: true
      extension: 0.0
    - name: rear_bumper
      type: a200.bumper
      model: default
      parent: rear_bumper_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      enabled: true
      extension: 0.0
    - name: top_plate
      type: a200.top_plate
      model: pacs
      parent: default_mount
      xyz: [0.0, 0.0, 0.0]
      rpy: [0.0, 0.0, 0.0]
      enabled: true
  extras:
    urdf: {}
```

You should replace the example serial number and any platform-specific values with the ones appropriate for your setup.

### 9.4 Generate the Clearpath setup script

```bash
source /opt/ros/jazzy/setup.bash
ros2 run clearpath_generator_common generate_bash -s ~/clearpath
source ~/clearpath/setup.bash
```

Optionally add the following line to `~/.bashrc`:

```bash
source ~/clearpath/setup.bash
```

### 9.5 Launch the official simulator

```bash
source /opt/ros/jazzy/setup.bash
source ~/clearpath/setup.bash
ros2 launch clearpath_gz simulation.launch.py setup_path:=$HOME/clearpath
```

At this point, validate that:

- the Husky appears correctly
- the namespace matches the one from `robot.yaml`
- control works
- the robot responds to `cmd_vel`

---

## 10. Driving the official Husky A200 simulator

### 10.1 Keyboard teleoperation

Install the keyboard teleop package:

```bash
sudo apt-get update
sudo apt-get install ros-jazzy-teleop-twist-keyboard
```

Run it like this:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
```

If your robot uses a namespace, apply it explicitly. Example:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r __ns:=/a200_0000
```

### 10.2 Command-line velocity command

You can also publish directly to `cmd_vel`:

```bash
ros2 topic pub /a200_0000/cmd_vel geometry_msgs/msg/TwistStamped \
"twist:
  linear:
    x: 0.3
    y: 0.0
    z: 0.0
  angular:
    x: 0.0
    y: 0.0
    z: 0.0"
```

If the robot does not move:

- make sure the simulation is not paused
- confirm the namespace
- confirm the topic type

Useful checks:

```bash
ros2 topic list | grep cmd_vel
ros2 topic info /a200_0000/cmd_vel
```

---

## 11. Integrating the official Husky A200 into `lar_gazebo`

The most practical strategy is:

1. launch the **LAR laboratory world** using `lar_gazebo`
2. use the **official Clearpath robot-generation / spawn workflow** for the Husky
3. keep the robot configuration in `~/clearpath/robot.yaml`

A wrapper launch such as `lar_husky_a200.launch.py` can be used to:

- launch the LAR world with `ros_gz_sim`
- preserve `GZ_SIM_RESOURCE_PATH` for the laboratory models
- include Clearpath's robot spawn launch with the same `setup_path`

This keeps the laboratory world in your package while still relying on the official Clearpath robot stack.

### Important note

If you use Clearpath extras from a package built in a workspace, that workspace should be added to `system.ros2.workspaces` in `robot.yaml`.

---

## 12. Suggested workflow for Husky + laboratory integration

Recommended order:

1. validate `lar_gazebo` alone in Rolling + Jetty
2. validate Husky A200 alone in the official Clearpath simulator workflow
3. only then combine the two
4. add navigation, sensors, or custom payloads after the base integration is stable

This avoids debugging the world, the robot, and the simulator stack all at the same time.

---

## 13. Troubleshooting

### Gazebo opens but models are missing

Check `GZ_SIM_RESOURCE_PATH`.

### Some models are black

This often indicates unsupported legacy material scripts.

### Gazebo crashes while loading a model

Check whether the model uses:

- detailed mesh collisions
- malformed mesh geometry
- legacy material/script resources

Simplified collisions are usually more robust.

### Gazebo rendering issues

Gazebo Sim uses Ogre 2 and expects modern OpenGL support. If necessary, try:

```bash
export LIBGL_DRI3_DISABLE=1
```

or

```bash
export LIBGL_ALWAYS_SOFTWARE=1
```

---

## 14. Creating and publishing the `rolling-devel` branch

If you already have the migrated repository locally, the usual flow is:

```bash
cd ~/lar_gazebo_ws/src/lar_gazebo
git status
git switch -c rolling-devel
git add .
git commit -m "Migrate lar_gazebo to ROS 2 Rolling and Gazebo Jetty"
git push -u origin rolling-devel
```

If `rolling-devel` already exists remotely and you only want to track it locally:

```bash
git fetch origin
git switch --track origin/rolling-devel
```

---

## 15. Recommended next steps

After publishing this branch, the recommended next steps are:

1. stabilize the LAR world models in Gazebo Jetty
2. keep Husky validation on the official Clearpath path
3. maintain the Husky integration as a wrapper layer, not by forking large parts of the official Clearpath stack unless really necessary

---

## 16. License and attribution

This branch is based on the original `lar_gazebo` repository and adapts it to ROS 2 / Gazebo Sim workflows.

Please keep the original attribution and repository license information.

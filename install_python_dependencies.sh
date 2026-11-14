
#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "Run with: source src/install_python_dependencies.sh"
    exit 1
fi

_sally_install_dependencies() {
    local script_dir workspace_dir deps_dir requirements_file

    script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || return 1

    # Support flat and nested ROS 2 workspace layouts.
    if [[ "$(basename -- "$script_dir")" == "src" ]]; then
        workspace_dir="$(dirname -- "$script_dir")"
    elif [[ "$(basename -- "$(dirname -- "$script_dir")")" == "src" ]]; then
        workspace_dir="$(dirname -- "$(dirname -- "$script_dir")")"
    else
        echo "Error: Project must be inside a ROS 2 workspace src directory."
        return 1
    fi

    deps_dir="$workspace_dir/.sally_deps"
    requirements_file="$script_dir/requirements-hardware.txt"

    if [[ ! -f "$requirements_file" ]]; then
        echo "Error: Missing $requirements_file"
        return 1
    fi

    if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
        echo "Error: ROS 2 Jazzy not found."
        return 1
    fi

    # Load ROS 2 and use system Python.
    source /opt/ros/jazzy/setup.bash || return 1

    # Install hardware dependencies into an isolated directory.
    echo "Installing SALLY hardware dependencies..."

    /usr/bin/python3 -m pip install \
        --disable-pip-version-check \
        --upgrade \
        --target "$deps_dir" \
        -r "$requirements_file" || return 1

    # Make dependencies available to ROS 2 Python nodes.
    export PYTHONPATH="$deps_dir${PYTHONPATH:+:$PYTHONPATH}"

    # Install ROS 2 system dependencies.
    echo "Installing ROS 2 dependencies..."

    rosdep install \
        --from-paths "$workspace_dir/src" \
        --ignore-src \
        --rosdistro jazzy \
        -y \
        --skip-keys="ament_python python3-adafruit-blinka-pip python3-adafruit-circuitpython-motor-pip python3-adafruit-circuitpython-pca9685 python3-adafruit-blinka python3-board" || return 1

    # Verify hardware library imports.
    echo "Checking hardware dependencies..."

    /usr/bin/python3 -c \
        'import board, adafruit_pca9685, adafruit_motor.servo; print("SALLY hardware dependencies OK")' || return 1

    echo "SALLY environment ready!"
}

_sally_install_dependencies

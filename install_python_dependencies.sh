cd ~/sally_ws

# Install Python dependencies outside the system Python directories
python3 -m pip install \
    --target "$PWD/.sally_deps" \
    -r src/requirements-hardware.txt

# Make dependencies visible to the ROS 2 Python interpreter
export PYTHONPATH="$PWD/.sally_deps${PYTHONPATH:+:$PYTHONPATH}"

# Install ROS dependencies, skipping the pip packages installed above
rosdep install \
    --from-paths src/PROJECT-SALLY-/sally_teleop \
    --ignore-src \
    --rosdistro jazzy \
    -y \
    --skip-keys="python3-adafruit-blinka-pip python3-adafruit-circuitpython-motor-pip"
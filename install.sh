#!/bin/bash
set -e

ROS_DISTRO=${ROS_DISTRO:-jazzy}

echo "╔══╣ Install: Ollama ROS (STARTING) ╠══╗"

sudo apt-get update
sudo apt-get install -y zstd xterm

if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

python3 -m pip install --break-system-packages ollama

cd ../
if [ ! -d sobits_interfaces ]; then
  git clone -b "${ROS_DISTRO}-devel" https://github.com/TeamSOBITS/sobits_interfaces.git
fi
cd sobits_interfaces
bash install.sh
cd ..

echo "╚══╣ Install: Ollama ROS (FINISHED) ╠══╝"

#!/bin/bash

echo "╔══╣ Install: Ollama ROS (STARTING) ╠══╗"


curl -fsSL https://ollama.com/install.sh | sh

python3 -m pip install ollama

sudo apt-get update
sudo apt install -y xterm

cd ../
git clone -b $ROS_DISTRO-devel https://github.com/TeamSOBITS/sobits_interfaces.git
cd sobits_interfaces
bash install.sh
cd ..

echo "╚══╣ Install: Ollama ROS (FINISHED) ╠══╝"

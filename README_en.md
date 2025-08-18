<a name="readme-top"></a>

[JP](README.md) | [EN](README_en.md)

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

# Ollama for ROS

<!-- Table of Contents -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#introduction">Introduction</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#launch-and-usage">Launch and Usage</a></li>
      <ul>
        <li><a href="#model-download">Model Download</a></li>
        <li><a href="#conversation">Conversation</a></li>
      </ul>
    </li>
    <li><a href="#milestones">Milestones</a></li>
    <!-- <li><a href="#contributing">Contributing</a></li> -->
    <!-- <li><a href="#license">License</a></li> -->
    <li><a href="#references">References</a></li>
  </ol>
</details>



<!-- Introduction -->
## Introduction

This repository provides a package that allows Large Language Models (LLMs) to run offline locally.

Processing speed varies depending on whether a CPU or GPU is used, but some models run smoothly even on a CPU.

Specifically, since LLMs construct responses word by word, there is an intermediate process between the call and the final response. 

Therefore, this package uses ROS2 Action communication to handle this.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- Getting Started -->
## Getting Started

This section explains how to set up this repository.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Prerequisites

First, ensure you have the following environment set up before proceeding to the installation steps.

| System | Version |
| --- | --- |
| Ubuntu | 22.04 (Jammy Jellyfish) |
| ROS    | Humble Hawksbill    |
| Python | >=3.10              |

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Installation

1. Navigate to your ROS2 src folder.
    ```sh
    cd ~/colcon_ws/src/
    ```
2. Clone this repository.
    ```sh
    git clone -b humble-devel https://github.com/TeamSOBITS/ollama_ros
    ```
3. Move into the repository directory.
    ```sh
    cd ollama_ros/
    ```
4. Install dependencies.
    ```sh
    bash install.sh
    ```
5. Compile the package.
    ```sh
    cd ~/colcon_ws/
    ```
    ```sh
    colcon build --symlink-install
    ```
    ```sh
    source ~/colcon_ws/install/setup.sh
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- Launch and Usage -->
## Launch and Usage

This section explains how to use this repository.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Model Download

1. Launch [model_download.launch.py](launch/model_download.launch.py).
    ```sh
    ros2 launch ollama_ros model_download.launch.py
    ```
2. Download the desired model from the GUI.\
  Click [download] to download the model.

> [!NOTE]
> This is not an exhaustive list of all models; these are selected from [here](https://ollama.com/library).\
> (Listing all would make the GUI too large and make it difficult to adapt to official updates).

If you want to download a model not available in the GUI, add it to [/models/model_list.yaml](models/model_list.yaml).

Example: If you want to download the deepseek-r1 model with 14b parameters.

```
models:
  - "deepseek-r1:14b"
```

If a model is already downloaded, you can delete ([delete]), copy ([copy]), or push ([push]) it.

> [!WARNING]
> Model downloads may take some time. Please wait until the GUI updates.

<div align="center">
  <img src="img/download_demo.png" height="420">
</div>

> [!NOTE]
> For more details and specific operations, please refer to the  [original ollama-python](https://github.com/ollama/ollama-python) and [ollama](https://github.com/ollama/ollama) repositories.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Conversation

1. Start the Server by launching [ollama.launch.py](launch/ollama.launch.py)．
   ```sh
   ros2 launch ollama_ros ollama.launch.py
   ```
2. Start the Server by launching.

> [!WARNING]
> Processing may be slow on a CPU, so it might be better to wait while observing the progress via Action communication.

> [!NOTE]
> For details on setting up pre-prompts and `room_name`, please refer to [here](README_DETAILS_en.md).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- Milestones -->
## Milestones
See the [Issues page][issues-url] for current bugs and feature requests.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- References -->
## References

* [ollama](https://ollama.com/)
* [ollama-python.git](https://github.com/ollama/ollama-python)
* [ollama.git](https://github.com/ollama/ollama)
* [Models](https://ollama.com/library)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/TeamSOBITS/ollama_python.svg?style=for-the-badge
[contributors-url]: https://github.com/TeamSOBITS/ollama_python/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/TeamSOBITS/ollama_python.svg?style=for-the-badge
[forks-url]: https://github.com/TeamSOBITS/ollama_python/network/members
[stars-shield]: https://img.shields.io/github/stars/TeamSOBITS/ollama_python.svg?style=for-the-badge
[stars-url]: https://github.com/TeamSOBITS/ollama_python/stargazers
[issues-shield]: https://img.shields.io/github/issues/TeamSOBITS/ollama_python.svg?style=for-the-badge
[issues-url]: https://github.com/TeamSOBITS/ollama_python/issues
[license-shield]: https://img.shields.io/github/license/TeamSOBITS/ollama_python.svg?style=for-the-badge
[license-url]: LICENSE

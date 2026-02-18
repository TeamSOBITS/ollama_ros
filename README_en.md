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
    <li><a href="#model-download">Model Download</a></li>
    <li><a href="#launch-and-usage">Launch and Usage</a></li>
    <li><a href="#sending-requests-to-the-server">Sending Requests to the Server</a></li>
        <li><a href="#function-calling">Function Calling</a></li>
    </li>
    <li><a href="#milestones">Milestones</a></li>
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

- If you want to download a model not available in the GUI, add it to [/models/model_list.yaml](models/model_list.yaml).
  - Example: If you want to download the deepseek-r1 model with 14b parameters.
    ```yaml
    models:
      - "deepseek-r1:14b"
    ```
- If a model is already downloaded, you can delete ([delete]), copy ([copy]), or push ([push]) it.

> [!WARNING]
> Model downloads may take some time. Please wait until the GUI updates.

<div align="center">
  <img src="img/download_demo.png" height="420">
</div>

> [!NOTE]
> For more details and specific operations, please refer to the  [original ollama-python](https://github.com/ollama/ollama-python) and [ollama](https://github.com/ollama/ollama) repositories.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- Launch and Usage -->
## Launch and Usage
1. Update the model settings in [prompt/base_prompt.yaml](prompt/base_prompt.yaml) according to your needs.
    ```yaml
    /**:
      ros__parameters:
        ollama:
          num_ctx: 4096          # Context window (memory capacity). Amount of previous conversation and image data to retain (in tokens).
          num_predict: 4096      # Maximum tokens to predict. Limits the length of the AI's response in a single request.
          repeat_last_n: 64      # Range for repetition suppression. How many recent tokens to check for repeated phrases.
          repeat_penalty: 1.1    # Strength of repetition suppression. Values > 1.0 prevent looping (e.g., 1.1 to 1.5).
          temperature: 0.7       # Generation randomness (temperature). Closer to 0 for factual/fixed; closer to 1 for creative/random.
          top_k: 40              # Vocabulary filtering. Limits candidate words to the top 40 most probable tokens to reduce nonsense.
          top_p: 0.9             # Cumulative probability filtering. Selects from words whose sum of probabilities reaches 90%.
          seed: 42               # Random seed. Fixed value ensures deterministic (reproducible) responses (-1 for random).
          json_mode: false       # Force JSON mode. Ensures output is a valid JSON (requires system prompt adjustment).
          tool_choice: "none"    # Tool (function) calling mode. "none" to disable, "required" to force, "auto" for AI to decide.
    ```

* Parameters can also be modified after launching [ollama.launch.py](launch/ollama.launch.py).
  * Example: Changing `tool_choice` to `auto`:
    ```sh
    ros2 param set /ollama_action_server ollama.tool_choice auto
    ```

2. [Optional] Define "rooms" in [prompt/base_prompt.yaml](prompt/base_prompt.yaml) for context engineering.
    ```yaml
    example_room: # Room name
    # system: Define the LLM's character and constraints (role, tone, rules).
    - {system: "You are the guide robot 'SOBIT'. Please respond in polite Japanese."}

    # user: Human (user) query (images can be attached via the 'files' key).
    - {user: "Hello! What can you do?", files: ["sobit_mini.png"]}

    # model: LLM response (used to maintain the conversation flow).
    - {model: "Hello! I am SOBIT. I can provide facility guidance and perform image recognition."}
    ```

    ```yaml
    # Example: Chatbot for introducing your team
    team_introduce:               # Another room named 'team_introduce'
      - {user : "Our team is a student organization called SOBITS!"}  # Example without images
      - {model: "SOBITS! That sounds like a wonderful name. What kind of team is it?"}
      - {user : "We have 40 members ranging from undergraduates to PhD students!"}
      - {model: "40 members! That's quite a large student team. With such a diverse group, it sounds like an amazing environment for sharing perspectives and knowledge."}
    ```

3. Launch the Action Server by running [ollama.launch.py](launch/ollama.launch.py).
    ```sh
    ros2 launch ollama_ros ollama.launch.py
    ```

> [!WARNING]
> Processing may be slow on a CPU, so it might be better to wait while observing the progress via Action communication.

> [!NOTE]
> For details on setting up pre-prompts and `room_name`, please refer to [here](README_DETAILS_en.md).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Sending Requests to the Server

Requests are sent to the Ollama server using the `sobits_interfaces/action/ChatLlmRecognition` action.

| Item | Field Name | Type | Description |
| --- | --- | --- | --- |
| **Action Name** |  |  | `ollama_action` |
| **Goal** | `room_name` | string | Arbitrary room name to manage conversation history. |
|  | `request` | string | Text message from the user. |
|  | `image` | sensor_msgs/Image[] | List of image messages to send. |
|  | `sound_file_path` | string[] | List of file paths to send. |
|  | `model_name` | string | Name of the model to use (e.g., "deepseek-r1:14b"). |
|  | `is_stack` | bool | Whether to push the current exchange to the conversation history. |
| **Result** | `result` | string | Response text from Ollama. |

<p align="right">(<a href="#readme-top">Back to top</a>)</p>

## Function Calling

This feature allows the LLM to analyze user instructions and call predefined functions when appropriate. The LLM outputs the function name and arguments to be executed in JSON format.

1. Define the functions you want to use in [ollama_tools.yaml](./prompt/ollama_tools.yaml).
* Ensure the `description` is clear and concise.
* Describing what each parameter expects helps the model provide the correct arguments.

    ```yaml
    tools: # List of tool definitions available to the LLM
      - type: "function" # Type of tool (currently fixed to "function")
        function:
          name: "navigation" # Function name: Unique identifier used on the program side
          description: "Moves the robot to a specified room or location." # Instruction to LLM: Description of when to use this function
          parameters: # Definition of arguments to pass to the function
            type: "object" # Argument data structure (usually "object")
            properties: # Specific argument details
              location: # Argument name
                type: "string" # Argument type (string)
                description: "Name of the destination (e.g., kitchen, living room)." # Explanation for the LLM on what to input
            required: ["location"] # List of arguments required for execution

      - type: "function"
        function:
          name: "object_detect"
          description: "Detects all objects currently visible in the robot's camera and returns a list."
          parameters:
            type: "object"
            properties: {} # Specify an empty object if no arguments are needed
            required: [] # No required parameters
    ```

2. Change the `tool_choice` parameter in [ollama_config.yaml](prompt/ollama_config.yaml) to one of the following:
    * `required`: Forces the LLM to call some function (tool).
    * `auto`: The LLM automatically decides whether to call a function or respond with text based on the context.

3. Launch the Ollama ROS Action Server.
    ```sh
    ros2 launch ollama_ros ollama.launch.py
    ```
4. Send a request from the client.
* Example: If the request is "Please go to the kitchen.", the following JSON string format will be returned as output. Please parse this string on the client side for use.
    ```text
    TOOL_CALL:[{"name": "navigation", "args": {"location": "kitchen"}}]
    ```

<p align="right">(<a href="#readme-top">Back to top</a>)</p>

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

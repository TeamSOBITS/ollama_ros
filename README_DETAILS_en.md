<a name="readme-top"></a>

[JP](README_DETAILS.md) | [EN](README_DETAILS_en.md)

<sub>[Back to README](README_en.md)</sub>

## Details

### About Message Type

The structure of the message called via Action communication is as follows:
```sh
# ChatLlmRecognition.action
# Goal
string room_name             # Specify room name
string request               # Request message
sensor_msgs/Image[] image    # List of input images
string[] sound_file_path     # List of paths to input audio files
string model_name            # Name of the model
bool is_stack                # Whether to remember this interaction in room_name
---
# Result
string result                # Reply message
float64 elapsed_time         # Time taken for the reply in seconds
---
# Feedback
string wip_result            # Work-in-progress message
bool end_flag                # Whether the transmission of work-in-progress message has ended
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### What is `room_name`?

`room_name` is a label used to assign conversation history.
For example, in ChatGPT, you can switch rooms for each conversation.

Here's an example of such a state:

```yaml
# Room A
USER : Tell me about SOBITS.
GPT : As a large language model, I don't have knowledge about specific words.
USER : I see. SOBITS is a team composed of students from Soka University's Cui Lab and Hagiwara Lab.
GPT : Oh, I see! A joint team from two laboratories sounds wonderful!

# Room B
USER : Please answer a question about mathematics.
GPT : Certainly. What kind of math question do you have?
USER : Why can't you divide by 0?
GPT : Division by zero is not mathematically defined, so it is meaningless.
```

Suppose we have these two rooms, A and B.

If the user asks "What is SOBITS?" in these two rooms, GPT in Room A can naturally answer it.

Here are example responses:

```yaml
# Room A
USER : What is SOBITS?
GPT : You just told me about SOBITS. It's a joint team from the Cui Lab and Hagiwara Lab, right? Was there a mistake?

# Room B
USER : What is SOBITS?
GPT : I don't have any knowledge about SOBITS. I might be able to answer if it's a math question.
```
In this package, `room_name` corresponds to these Room A and Room B.\
You can create any number of `room_name`s, and as long as the Server launch is not terminated, you can continue conversations in a previously specified room by simply designating its name.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Defining Pre-prompts
As with `room_name` above, you can pre-define conversation history as if you had a prior conversation.\
This can typically be defined in [base_prompt.yaml](prompt/base_prompt.yaml).

Inside, as an example, it is defined as follows:

```yaml
# YAML file where conversations can be pre-defined
sobit_mini:                                          # In the room named sobit_mini...
- {user      : "My name is SOBIT MINI."}             # If the User says "My name is SOBIT MINI.", then...
- {assistant: "Nice to meet you SOBIT MINI!"}        # Since the conversation "Nice to meet you, SOBIT MINI!" is pre-defined,
                                                     # you can continue the conversation from this point by specifying the room name 'sobit_mini'.

team_introduce:                                      # Another room named team_introduce is also prepared
- {user      : "Our team name is SOBITS."}
- {assistant: "I love it! SOBITS sounds like a unique and fun team name."}
- {user      : "SOBITS consists of about 30 people."}
- {assistant: "A team of 30 people! That's impressive!"}

```

In the sobit_mini `room_name`, the conversation can proceed with the system recognizing the User's name as SOBIT MINI.

In another room, team_introduce, the system knows the team name and the number of people in the team because it contains an explanation about the SOBITS team.

Based on this, let's explain a simple way to use rooms and pre-prompts.

1. Start the ActionServer.
    ```sh
    ros2 launch ollama_ros ollama.launch.py
    ```

2. Execute the Action Client.

Set `room_name` to `default` and type "Do you know my name?" in `request`.

<div align="left">
<img src="img/default_result.png" height="420">
</div>

Since the `default` room is not in the pre-prompts and was just defined, the reply should have been "I don't know."

Now, run the client again.

This time, set `room_name` to sobit_mini and similarly set request to "Do you know my name?".

<div align="left">
<img src="img/sobit_mini_result.png" height="420">
</div>

You should have received a reply similar to "Your name is SOBIT MINI."\
This is because conversation history is accumulated for each room. \
As long as the Server launch is not terminated, you can resume conversations from pre-prompts or previous interactions simply by specifying the room name.

> [!IMPORTANT]
> Depending on the model used, you can send not only text but also images and audio.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

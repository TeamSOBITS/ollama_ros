import yaml

yaml_path = "/home/sobits/colcon_ws/src/ollama_python/prompt/base_prompt.yaml"
with open(yaml_path, "r") as file:
    prompt_ = yaml.safe_load(file)

print(prompt_)

# prompt_ = {'sobit_mini': [{'user': 'My name is SOBIT MINI. I am a robot like this picture.', 'image': ['sobit_mini.png']},
#                           {'assistant': 'Nice to meet you SOBIT MINI! You have big eyes and a pretty appearance with two arms like a human being!'}],
#            'team_introduce': [{'user': 'Our team name is SOBITS.'},
#                               {'assistant': 'I love it! SOBITS sounds like a unique and fun team name.'},
#                               {'user': 'SOBITS consists of about 30 people.'},
#                               {'assistant': "A team of 30 people! That's impressive!"}]
#             }


yaml_folder_path = "/".join(yaml_path.split("/")[:-1]) +"/"


chat_messages_ = {}
for rn in prompt_.keys():
    chat_messages_[str(rn)] = []
    for talk in prompt_[rn]:
        if ("user" in list(talk.keys())):
            chat_messages_[str(rn)] += [{"role": "user", "content": talk["user"]}]
            if ("image" in list(talk.keys())):
                chat_messages_[str(rn)][-1]["image"] = []
                for img in talk["image"]:
                    if (img[0] == "/"):
                        chat_messages_[str(rn)][-1]["image"] += [img]
                    else:
                        chat_messages_[str(rn)][-1]["image"] += [yaml_folder_path + img]
        else:
            chat_messages_[str(rn)] += [{"role": "assistant", "content": talk["assistant"]}]

print("===")
print(chat_messages_)

chat_messages_ = {'sobit_mini':     [{'role': 'user', 'content': 'My name is SOBIT MINI. I am a robot like this picture.', 'image': ['/home/sobits/colcon_ws/src/ollama_python/prompt/sobit_mini.png']},
                                     {'role': 'assistant', 'content': 'Nice to meet you SOBIT MINI! You have big eyes and a pretty appearance with two arms like a human being!'}],
                  'team_introduce': [{'role': 'user', 'content': 'Our team name is SOBITS.'},
                                     {'role': 'assistant', 'content': 'I love it! SOBITS sounds like a unique and fun team name.'},
                                     {'role': 'user', 'content': 'SOBITS consists of about 30 people.'},
                                     {'role': 'assistant', 'content': "A team of 30 people! That's impressive!"}],
                  'addition':       [{'role': 'user', 'content': 'Our team name is SOBITS.', 'image': ['/home/sobits/colcon_ws/src/ollama_python/images/icon.jpg', '/home/sobits/colcon_ws/src/ollama_python/prompt/girl.jpg']},
                                     {'role': 'assistant', 'content': 'I love it! SOBITS sounds like a unique and fun team name.'},
                                     {'role': 'user', 'content': 'SOBITS consists of about 30 people.'},
                                     {'role': 'assistant', 'content': "A team of 30 people! That's impressive!"}]}
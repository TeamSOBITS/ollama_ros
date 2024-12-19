import ollama

chat_stack = [{'role': 'user', 'content': 'What is the difference between these two images?', 'images': ["img1.jpg", "girl.jpg"]}]

while True:
    # vision = input("True or False : ")
    # text = input("input text >> ")
    # if ((vision == "True") or (vision == "true") or (vision == "")):
    #     img_path = input("image path >> ")
    #     chat_stack += [{'role': 'user', 'content': str(text), 'images': [str(img_path)]}]
    # else:
    #     chat_stack += [{'role': 'user', 'content': str(text)}]
    response = ollama.chat(
        model='llama3.2-vision',
        messages=chat_stack
    )

    # print(response["message"]["content"])
    chat_stack += [response["message"]]
    print("=====")
    print(chat_stack)
    print("=====")
    break

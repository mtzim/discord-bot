def open_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def setup_personality():
    """
    Setup the personality for the openai GPT model
    """

    conversation = list()
    conversation.append({"role": "system", "content": open_file("prompt.txt")})
    conversation.append(
        {"role": "user", "content": "Who won the world series in 2020?"}
    )
    conversation.append(
        {
            "role": "assistant",
            "content": "The Los Angeles Dodgers won the World Series in 2020.",
        }
    )
    return conversation

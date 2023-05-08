import os


def open_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def setup_personality(prompt=None):
    """
    Setup the personality for the openai GPT model
    """

    conversation = list()

    if not prompt:
        filepath = os.path.join(os.path.dirname(__file__), "prompt.txt")
        conversation.append({"role": "system", "content": open_file(f"{filepath}")})
        conversation.append(
            {"role": "user", "content": "Who won the world series in 2020?"}
        )
        conversation.append(
            {
                "role": "assistant",
                "content": "The Los Angeles Dodgers won the World Series in 2020.",
            }
        )
    else:
        conversation.append({"role": "system", "content": f"{prompt}"})

    return conversation

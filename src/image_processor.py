import os
import json
import base64
from openai import OpenAI


def load_api_key():
    """Loads the OpenAI API key from the config file."""
    # Build the path to the config file relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, "config", "openai_api.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}. Please create it.")

    with open(config_path, 'r') as f:
        config = json.load(f)
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("API key not found in config/openai_api.json")
        return api_key


def encode_image_to_base64(image_path):
    """Encodes a local image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_image_for_serial_number(image_path):
    """
    Sends an image to the OpenAI Vision API and asks for the serial number.

    :param image_path: The path to the image file.
    :return: The extracted serial number as a string, or an error message.
    """
    try:
        api_key = load_api_key()
        client = OpenAI(api_key=api_key)

        base64_image = encode_image_to_base64(image_path)

        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze the provided image of a car part."
                                    "Find the most prominent serial number or part number."
                                    "Return ONLY the number itself, with no extra text, labels, or explanations."
                                    "Try to avoid VDO number."
                                    "If no number is clearly visible, return the word 'None'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=500  # Restrict the output length
        )

        return response.choices[0].message.content.strip()

    except FileNotFoundError as e:
        return f"Error: {e}"
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"An unexpected API error occurred: {e}"
import json

def getFilepath() -> str:
    try:
        with open("config.json") as f:
            config = json.load(f)
            return config["filepath"]
    except FileNotFoundError:
        print("Config file does not found")
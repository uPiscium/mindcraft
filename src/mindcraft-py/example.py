import copy
import json
import os

from mindcraft_py import create_agent, init, wait


def main():
    init()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.abspath(
        os.path.join(script_dir, "..", "..", "agents", "Andy.json")
    )

    try:
        with open(profile_path, "r", encoding="utf-8") as file_obj:
            profile_data = json.load(file_obj)

        settings = {"profile": profile_data}
        create_agent(settings)

        settings_copy = copy.deepcopy(settings)
        settings_copy["profile"]["name"] = "andy2"
        create_agent(settings_copy)
    except FileNotFoundError:
        print(f"Error: Could not find profile at {profile_path}")

    wait()


if __name__ == "__main__":
    main()

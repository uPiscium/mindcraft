import copy
import json

from .config import resolve_settings
from .runtime import MindcraftRuntime


def run_from_cli_args(cli_args=None):
    settings = resolve_settings(cli_args=cli_args)
    runtime = MindcraftRuntime()

    runtime.init(
        port=settings["mindserver_port"],
        host_public=True,
        auto_open_ui=settings["auto_open_ui"],
    )

    for profile_path in settings["profiles"]:
        with open(profile_path, "r", encoding="utf-8") as file_obj:
            profile_json = json.load(file_obj)

        agent_settings = copy.deepcopy(settings)
        agent_settings["profile"] = profile_json
        runtime.create_agent(agent_settings)

    runtime.wait()

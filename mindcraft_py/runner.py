import copy

from .config import resolve_settings
from .profiles import load_profile
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
        profile_json = load_profile(profile_path)

        agent_settings = copy.deepcopy(settings)
        agent_settings["profile"] = profile_json
        runtime.create_agent(agent_settings)

    runtime.wait()

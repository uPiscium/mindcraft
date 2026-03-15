import json
import os
import subprocess


def resolve_settings(cli_args=None, env=None):
    if cli_args is None:
        cli_args = []
    if env is None:
        env = os.environ.copy()

    script_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "src",
            "mindcraft-py",
            "resolve-settings.js",
        )
    )

    command = ["node", script_path, *cli_args]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "unknown error"
        raise RuntimeError(f"Failed to resolve settings via Node.js bridge: {stderr}")

    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Node.js bridge returned invalid JSON for settings"
        ) from error

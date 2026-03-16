import subprocess


SUPPORTED_NODE_MAJORS = {18, 20, 22}


def _parse_node_major(version_output):
    version = version_output.strip()
    if version.startswith("v"):
        version = version[1:]
    major_text = version.split(".", 1)[0]
    return int(major_text)


def resolve_node_executable(env=None):
    if env is None:
        env = None

    candidates = []
    explicit_node = None
    if env:
        explicit_node = env.get("MINDCRAFT_NODE_BIN")
    if explicit_node:
        candidates.append(explicit_node)

    candidates.extend(["node22", "node20", "node18", "node"])

    best_unsupported = None
    for candidate in candidates:
        try:
            completed = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
        except FileNotFoundError:
            continue

        if completed.returncode != 0:
            continue

        raw_version = completed.stdout.strip() or completed.stderr.strip()
        try:
            major = _parse_node_major(raw_version)
        except (TypeError, ValueError):
            continue

        if major in SUPPORTED_NODE_MAJORS:
            return candidate

        if best_unsupported is None:
            best_unsupported = (candidate, raw_version)

    if best_unsupported:
        node_bin, node_version = best_unsupported
        raise RuntimeError(
            "Unsupported Node.js version detected for Mindcraft Python bridge "
            f"({node_bin} -> {node_version}). Use Node.js 18 or 20 LTS, or set "
            "MINDCRAFT_NODE_BIN to a compatible Node binary."
        )

    raise RuntimeError(
        "Node.js executable not found. Install Node.js 18 or 20 LTS, or set "
        "MINDCRAFT_NODE_BIN to your Node binary path."
    )

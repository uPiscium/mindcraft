from __future__ import annotations

import time

from mindcraft_py.agent_process import AgentProcess
from mindcraft_py.mindserver_state import MindserverState
from mindcraft_py.node_runtime import NodeRuntimeProcess
from mindcraft_py.task_coordinator import CentralTaskCoordinator


class MindcraftRuntime:
    def __init__(self):
        self.port = None
        self.host_public = False
        self.auto_open_ui = False
        self.agents = MindserverState()
        self.node_runtime = NodeRuntimeProcess()
        self.agent_processes = {}
        self.task_pool = CentralTaskCoordinator()

    def init(self, port=8080, host_public=False, auto_open_ui=True, startup_timeout=20):
        self.port = port
        self.host_public = host_public
        self.auto_open_ui = auto_open_ui
        self.startup_timeout = startup_timeout

    def create_agent(self, settings, timeout=20):
        profile = settings.get("profile", {})
        name = profile.get("name")
        if not name:
            raise ValueError("Agent name is required in profile")
        self.agents.register_agent(settings, settings.get("viewer_port", 0))
        self.agents.set_in_game(name, True)
        return {"success": True, "error": None}

    def register_agent(self, settings, viewer_port):
        return self.agents.register_agent(settings, viewer_port)

    def get_agent(self, agent_name):
        return self.agents.get(agent_name)

    def start_agent(self, agent_name):
        agent = self.agent_processes.get(agent_name)
        if not agent:
            return None
        return agent["agent_process"].force_restart()

    def stop_agent_by_name(self, agent_name):
        agent = self.agent_processes.get(agent_name)
        if not agent:
            return None
        agent["agent_process"].stop()
        self.agents.set_in_game(agent_name, False)
        return True

    def destroy_agent(self, agent_name):
        agent = self.agent_processes.get(agent_name)
        if not agent:
            return None
        agent["agent_process"].stop()
        del self.agent_processes[agent_name]
        self.agents.remove(agent_name)
        return True

    def logout_agent(self, agent_name):
        return self.agents.set_in_game(agent_name, False)

    def agents_status(self):
        return self.agents.status()

    def set_agent_settings(self, agent_name, settings):
        return self.agents.set_settings(agent_name, settings)

    def get_settings(self, agent_name):
        agent = self.agents.get(agent_name)
        if not agent:
            return None
        return agent["settings"]

    def connect_agent_process(self, agent_name):
        return self.agents.set_socket(agent_name, True)

    def login_agent(self, agent_name):
        agent = self.agents.set_socket(agent_name, True)
        if agent:
            self.agents.set_in_game(agent_name, True)
        return agent

    def disconnect_agent(self, agent_name):
        agent = self.agents.set_socket(agent_name, False)
        if agent:
            self.agents.set_in_game(agent_name, False)
        return agent

    def set_full_state(self, agent_name, state):
        return self.agents.set_full_state(agent_name, state)

    def register_task(self, task=None, **task_fields):
        return self.task_pool.register_task(task, **task_fields)

    def list_tasks(self):
        return self.task_pool.list_tasks()

    def acquire_task(self, requester_id, capability):
        return self.task_pool.acquire_task(requester_id, capability)

    def yield_task(self, requester_id, task_id, reason):
        return self.task_pool.yield_task(requester_id, task_id, reason)

    def get_full_state(self, agent_name):
        agent = self.agents.get(agent_name)
        if not agent:
            return None
        return agent.get("full_state")

    def start_agent_process(self, settings):
        profile = settings.get("profile", {})
        name = profile.get("name")
        if not name:
            raise ValueError("Agent name is required in profile")

        profiles = (
            [settings.get("profile_path")] if settings.get("profile_path") else None
        )
        agent_process = AgentProcess(name, self.node_runtime)
        process = agent_process.start(profile_path=profiles[0] if profiles else None)
        self.agent_processes[name] = {
            "agent_process": agent_process,
            "process": process,
            "settings": settings,
            "count_id": settings.get("count_id", 0),
            "running": True,
            "last_restart": time.time(),
        }
        self.agents.set_process(name, agent_process)
        return process

    def create_agent_process(self, settings, mindserver_port):
        profile = settings.get("profile", {})
        name = profile.get("name")
        if not name:
            raise ValueError("Agent name is required in profile")
        if settings.get("mock_client"):
            return {
                "type": "mock",
                "name": name,
                "mindserver_port": mindserver_port,
                "settings": settings,
            }
        agent_process = AgentProcess(name, self.node_runtime)
        return {
            "type": "real",
            "name": name,
            "mindserver_port": mindserver_port,
            "settings": settings,
            "agent_process": agent_process,
        }

    def restart_agent_process(self, settings):
        profiles = (
            [settings.get("profile_path")] if settings.get("profile_path") else None
        )
        return self.node_runtime.restart(profiles=profiles)

    def restart_agent(self, agent_name):
        agent_entry = self.agent_processes.get(agent_name)
        if not agent_entry:
            return None
        if time.time() - agent_entry["last_restart"] < 10:
            raise RuntimeError(
                "Agent process exited too quickly and will not be restarted."
            )
        agent_entry["last_restart"] = time.time()
        agent_entry["agent_process"].force_restart()
        return agent_entry["agent_process"].process

    def mark_agent_exited(self, agent_name, code=None, signal=None):
        agent_entry = self.agent_processes.get(agent_name)
        if not agent_entry:
            return
        agent_entry["running"] = False
        agent_entry["exit_code"] = code
        agent_entry["exit_signal"] = signal

    def execute_query_command(self, agent_name, message, timeout=60):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        if message.startswith("!stats"):
            return (
                "STATS\n- Position: x: 0.00, y: 64.00, z: 0.00\n- Gamemode: "
                "creative\n- Health: 20 / 20\n- Hunger: 20 / 20\n- Biome: "
                "plains\n- Weather: Clear\n- Time: Morning\n- Current "
                "Action: Idle\n- Nearby Human Players: None.\n- Nearby Bot "
                "Players: None."
            )
        if message.startswith("!inventory"):
            return "INVENTORY: Nothing\nWEARING: Nothing"
        if message.startswith("!nearbyBlocks"):
            return "NEARBY_BLOCKS\n- grass_block\n- First Solid Block Above Head: air"
        if message.startswith("!entities"):
            return "NEARBY_ENTITIES: none"
        if message.startswith("!craftable"):
            return "CRAFTABLE_ITEMS\n- planks\n- sticks"
        if message.startswith("!modes"):
            return "MOdes\n- idle: on\n- gather: off"
        if message.startswith("!savedPlaces"):
            return "Saved place names: spawn, base"
        if message.startswith("!help"):
            return "Mock help is not implemented."
        return f"Unsupported mock query: {message}"

    def execute_action_command(self, agent_name, message, timeout=60):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        if message.startswith("!goal"):
            return "Goal set: mock."
        if message.startswith("!stop"):
            return "All actions stopped."
        if message.startswith("!newAction"):
            return "newAction executed in mock mode."
        return f"Unsupported mock action: {message}"

    def shutdown(self):
        self.agents.clear()
        self.task_pool.clear()

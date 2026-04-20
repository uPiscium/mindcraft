from __future__ import annotations

import time
import tomllib
from pathlib import Path

from mindcraft_py.agent_process import AgentProcess
from mindcraft_py.mindserver_state import MindserverState
from mindcraft_py.node_runtime import NodeRuntimeProcess
from mindcraft_py.task_coordinator import CentralTaskCoordinator
from mindcraft_py.task_slot import EMPTY, TaskSlotManager


class MindcraftRuntime:
    def __init__(self):
        self.port = None
        self.host_public = False
        self.auto_open_ui = False
        self.agents = MindserverState()
        self.node_runtime = NodeRuntimeProcess()
        self.agent_processes = {}
        self.agent_tasks = {}
        self.task_pool = CentralTaskCoordinator()
        self.task_slots = TaskSlotManager()

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
        self._seed_tasks_from_settings(settings)
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
        self._yield_agent_task(agent_name, "agent stopped")
        agent["agent_process"].stop()
        self.agents.set_in_game(agent_name, False)
        return True

    def destroy_agent(self, agent_name):
        agent = self.agent_processes.get(agent_name)
        if not agent:
            return None
        self._yield_agent_task(agent_name, "agent destroyed")
        agent["agent_process"].stop()
        del self.agent_processes[agent_name]
        self.agent_tasks.pop(agent_name, None)
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

    def register_tasks(self, tasks):
        return [self.register_task(task) for task in tasks or []]

    def replace_task_pool(self, tasks):
        self.task_pool.clear()
        return self.register_tasks(tasks)

    def load_task_pool_file(self, task_file_path):
        path = Path(task_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Task pool file not found: {path}")

        with path.open("rb") as handle:
            data = tomllib.load(handle)

        tasks = data.get("tasks")
        if not isinstance(tasks, list):
            raise ValueError("Task pool file must define a 'tasks' array.")

        registered = self.register_tasks(tasks)
        self._validate_task_dependencies()
        return registered

    def list_tasks(self):
        return self.task_pool.list_tasks()

    def acquire_task(self, requester_id):
        return self.task_pool.acquire_task(requester_id)

    def acquire_task_by_id(self, requester_id, task_id):
        return self.task_pool.acquire_task_by_id(requester_id, task_id)

    def acquire_task_for_agent(self, agent_name):
        agent = self.agent_processes.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        task = self.acquire_task(agent_name)
        self.agent_tasks[agent_name] = task
        agent["current_task"] = task
        self.task_slots.assign(agent_name, task)
        return task

    def yield_task(self, requester_id, task_id, reason):
        return self.task_pool.yield_task(requester_id, task_id, reason)

    def complete_task(self, requester_id, task_id, reason):
        return self.task_pool.complete_task(requester_id, task_id, reason)

    def get_ready_task_order(self):
        ordered = []
        completed = set()
        pending = {task["id"]: task for task in self.list_tasks()}

        while pending:
            progress = False
            for task_id in list(pending):
                task = pending[task_id]
                dependencies = task.get("depends_on", [])
                if all(dependency_id in completed for dependency_id in dependencies):
                    ordered.append(task_id)
                    completed.add(task_id)
                    pending.pop(task_id)
                    progress = True
            if not progress:
                break

        return ordered

    def yield_task_for_agent(self, agent_name, reason):
        agent_task = self.agent_tasks.get(agent_name)
        if not agent_task:
            return None
        result = self.yield_task(agent_name, agent_task["id"], reason)
        self.agent_tasks.pop(agent_name, None)
        agent = self.agent_processes.get(agent_name)
        if agent is not None:
            agent.pop("current_task", None)
        self.task_slots.fail(agent_name, reason)
        self.task_slots.clear(agent_name)
        return result

    def complete_task_for_agent(self, agent_name, reason):
        agent_task = self.agent_tasks.get(agent_name)
        if not agent_task:
            return None
        result = self.complete_task(agent_name, agent_task["id"], reason)
        self.agent_tasks.pop(agent_name, None)
        agent = self.agent_processes.get(agent_name)
        if agent is not None:
            agent.pop("current_task", None)
        self.task_slots.complete(agent_name, reason)
        self.task_slots.clear(agent_name)
        return result

    def get_task_slot(self, agent_name):
        return self.task_slots.get_slot(agent_name)

    def clear_task_slot(self, agent_name):
        self.task_slots.clear(agent_name)

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
        self._seed_tasks_from_settings(settings)
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
        self._yield_agent_task(agent_name, "agent exited")
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
        for agent_name in list(self.agent_tasks):
            self._yield_agent_task(agent_name, "runtime shutdown")
        self.agents.clear()
        self.task_pool.clear()

    def _seed_tasks_from_settings(self, settings):
        task_pool_file = settings.get("task_pool_file")
        if not task_pool_file:
            task_pool_file = settings.get("profile", {}).get("task_pool_file")
        if task_pool_file:
            self.load_task_pool_file(task_pool_file)
        tasks = settings.get("tasks")
        if tasks is None:
            tasks = settings.get("profile", {}).get("tasks")
        if tasks:
            self.register_tasks(tasks)

    def _yield_agent_task(self, agent_name, reason):
        try:
            return self.yield_task_for_agent(agent_name, reason)
        except Exception:
            return None

    def _validate_task_dependencies(self):
        task_ids = set(self.task_pool._tasks)
        for task in self.task_pool._tasks.values():
            missing_dependencies = [
                dependency_id
                for dependency_id in task.depends_on
                if dependency_id not in task_ids
            ]
            if missing_dependencies:
                raise ValueError(
                    f"Task '{task.id}' depends on missing task(s): "
                    f"{', '.join(missing_dependencies)}"
                )

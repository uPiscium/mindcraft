from __future__ import annotations


class MindserverState:
    def __init__(self):
        self.agents = {}

    def register_agent(self, settings, viewer_port):
        name = settings.get("profile", {}).get("name")
        if not name:
            raise ValueError("Agent name is required in profile")
        self.agents[name] = {
            "settings": settings,
            "viewer_port": viewer_port,
            "in_game": False,
            "socket_connected": False,
            "socket": None,
            "full_state": None,
            "process": None,
        }
        return self.agents[name]

    def get(self, agent_name):
        return self.agents.get(agent_name)

    def get_all(self):
        return self.agents

    def set_settings(self, agent_name, settings):
        agent = self.get(agent_name)
        if not agent:
            return None
        agent["settings"] = settings
        return agent

    def set_process(self, agent_name, process):
        agent = self.get(agent_name)
        if not agent:
            return None
        agent["process"] = process
        return agent

    def set_socket(self, agent_name, socket):
        agent = self.get(agent_name)
        if not agent:
            return None
        agent["socket"] = socket
        agent["socket_connected"] = bool(socket)
        return agent

    def set_in_game(self, agent_name, in_game):
        agent = self.get(agent_name)
        if not agent:
            return None
        agent["in_game"] = bool(in_game)
        return agent

    def set_full_state(self, agent_name, state):
        agent = self.get(agent_name)
        if not agent:
            return None
        agent["full_state"] = state
        return agent

    def remove(self, agent_name):
        if agent_name not in self.agents:
            return False
        del self.agents[agent_name]
        return True

    def clear(self):
        self.agents.clear()

    def status(self):
        return [
            {
                "name": name,
                "in_game": bool(agent.get("in_game")),
                "viewerPort": agent.get("viewer_port"),
                "socket_connected": bool(agent.get("socket_connected")),
            }
            for name, agent in self.agents.items()
        ]

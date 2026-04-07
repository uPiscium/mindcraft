from __future__ import annotations


class MindServerProxy:
    def __init__(self):
        self.agents = []

    def set_agents(self, agents):
        self.agents = agents or []

    def get_agents(self):
        return self.agents

    def get_num_other_agents(self):
        return max(len(self.agents) - 1, 0)


def send_bot_chat_to_server(agent_name, json_data):
    return {"agentName": agent_name, "json": json_data}


def send_output_to_server(agent_name, message):
    return {"agentName": agent_name, "message": message}

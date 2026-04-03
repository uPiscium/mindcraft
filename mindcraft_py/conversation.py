from __future__ import annotations


def compile_in_messages(convo):
    pack = {}
    full_message = ""
    while convo.in_queue:
        pack = convo.in_queue.pop(0)
        full_message += pack.get("message", "")
    pack["message"] = full_message
    return pack


def tag_message(message):
    return "(FROM OTHER BOT)" + message


class Conversation:
    def __init__(self, name):
        self.name = name
        self.active = False
        self.ignore_until_start = False
        self.blocked = False
        self.in_queue = []
        self.inMessageTimer = None

    def reset(self):
        self.active = False
        self.ignore_until_start = False
        self.in_queue = []
        self.inMessageTimer = None

    def queue(self, message):
        self.in_queue.append(message)


class ConversationManager:
    def __init__(self):
        self.convos = {}
        self.agent_names = []
        self.agents_in_game = []

    def update_agents(self, agents):
        self.agent_names = [agent["name"] for agent in agents]
        self.agents_in_game = [
            agent["name"] for agent in agents if agent.get("in_game")
        ]

    def get_in_game_agents(self):
        return list(self.agents_in_game)

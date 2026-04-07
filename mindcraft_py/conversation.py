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

    def end(self):
        self.active = False
        self.ignore_until_start = True
        return compile_in_messages(self)


class ConversationManager:
    def __init__(self):
        self.convos = {}
        self.agent_names = []
        self.agents_in_game = []
        self.active_conversation = None

    def update_agents(self, agents):
        self.agent_names = [agent["name"] for agent in agents]
        self.agents_in_game = [
            agent["name"] for agent in agents if agent.get("in_game")
        ]

    def _get_convo(self, name):
        if name not in self.convos:
            self.convos[name] = Conversation(name)
        return self.convos[name]

    def is_other_agent(self, name):
        return name in self.agent_names

    def other_agent_in_game(self, name):
        return name in self.agents_in_game

    def in_conversation(self, other_agent=None):
        if other_agent is not None:
            convo = self.convos.get(other_agent)
            return bool(convo and convo.active)
        return any(convo.active for convo in self.convos.values())

    def start_conversation(self, name):
        convo = self._get_convo(name)
        convo.reset()
        convo.active = True
        self.active_conversation = convo
        return convo

    def end_conversation(self, name):
        convo = self.convos.get(name)
        if not convo:
            return None
        ended = convo.end()
        if self.active_conversation and self.active_conversation.name == name:
            self.active_conversation = None
        return ended

    def end_all_conversations(self):
        for name in list(self.convos.keys()):
            self.end_conversation(name)

    def force_end_current_conversation(self):
        if not self.active_conversation:
            return None
        return self.end_conversation(self.active_conversation.name)

    def get_in_game_agents(self):
        return list(self.agents_in_game)

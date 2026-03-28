from __future__ import annotations


class MindcraftRuntime:
    def __init__(self):
        self.port = None
        self.host_public = False
        self.auto_open_ui = False
        self.agents = {}

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
        self.agents[name] = {
            "settings": settings,
            "mock_client": bool(settings.get("mock_client")),
            "in_game": True,
        }
        return {"success": True, "error": None}

    def execute_query_command(self, agent_name, message, timeout=60):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        if message.startswith("!stats"):
            return "STATS\n- Position: x: 0.00, y: 64.00, z: 0.00\n- Gamemode: creative\n- Health: 20 / 20\n- Hunger: 20 / 20\n- Biome: plains\n- Weather: Clear\n- Time: Morning\n- Current Action: Idle\n- Nearby Human Players: None.\n- Nearby Bot Players: None."
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

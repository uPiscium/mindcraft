const agentRegistry = {};

export function registerAgent(settings, viewer_port) {
    const name = settings.profile.name;
    agentRegistry[name] = {
        settings,
        viewer_port,
        in_game: false,
        socket_connected: false,
        socket: null,
        full_state: null,
        process: null,
    };
    return agentRegistry[name];
}

export function getAgent(agentName) {
    return agentRegistry[agentName] || null;
}

export function getAgents() {
    return agentRegistry;
}

export function setAgentSettings(agentName, settings) {
    if (!agentRegistry[agentName]) return null;
    agentRegistry[agentName].settings = settings;
    return agentRegistry[agentName];
}

export function setAgentSocket(agentName, socket) {
    if (!agentRegistry[agentName]) return null;
    agentRegistry[agentName].socket = socket;
    agentRegistry[agentName].socket_connected = Boolean(socket);
    return agentRegistry[agentName];
}

export function setAgentInGame(agentName, inGame) {
    if (!agentRegistry[agentName]) return null;
    agentRegistry[agentName].in_game = Boolean(inGame);
    return agentRegistry[agentName];
}

export function setAgentFullState(agentName, state) {
    if (!agentRegistry[agentName]) return null;
    agentRegistry[agentName].full_state = state;
    return agentRegistry[agentName];
}

export function setAgentProcess(agentName, process) {
    if (!agentRegistry[agentName]) return null;
    agentRegistry[agentName].process = process;
    return agentRegistry[agentName];
}

export function getAgentProcess(agentName) {
    return agentRegistry[agentName]?.process || null;
}

export function removeAgent(agentName) {
    if (!agentRegistry[agentName]) return false;
    delete agentRegistry[agentName];
    return true;
}

export function clearAgents() {
    for (const key of Object.keys(agentRegistry)) {
        delete agentRegistry[key];
    }
}

export function getAgentsStatus() {
    return Object.keys(agentRegistry).map((agentName) => {
        const agent = agentRegistry[agentName];
        return {
            name: agentName,
            in_game: Boolean(agent.in_game),
            viewerPort: agent.viewer_port,
            socket_connected: Boolean(agent.socket_connected),
        };
    });
}

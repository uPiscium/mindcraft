import { createMindServer, registerAgent, numStateListeners } from './mindserver.js';
import { createAgentProcess } from '../process/create_agent_process.js';
import open from 'open';
import { getAgentProcess as getAgentProcessRecord, getAgents, removeAgent, setAgentInGame, setAgentProcess } from './agent_registry.js';

let mindserver;
let connected = false;
let agent_count = 0;
let mindserver_port = 8080;

export async function init(host_public=false, port=8080, auto_open_ui=true) {
    if (connected) {
        console.error('Already initiliazed!');
        return;
    }
    mindserver = createMindServer(host_public, port);
    mindserver_port = port;
    connected = true;
    if (auto_open_ui) {
        setTimeout(() => {
            // check if browser listener is already open
            if (numStateListeners() === 0) {
                open('http://localhost:'+port);
            }
        }, 3000);
    }
}

export async function createAgent(settings) {
    if (!settings.profile.name) {
        console.error('Agent name is required in profile');
        return {
            success: false,
            error: 'Agent name is required in profile'
        };
    }
    settings = JSON.parse(JSON.stringify(settings));
    let agent_name = settings.profile.name;
    const agentIndex = agent_count++;
    const viewer_port = 3000 + agentIndex;
    registerAgent(settings, viewer_port);
    let load_memory = settings.load_memory || false;
    let init_message = settings.init_message || null;

    try {
        const agentProcess = createAgentProcess(agent_name, mindserver_port, settings);
        await agentProcess.start(load_memory, init_message, agentIndex, settings.profile_path);
        setAgentProcess(agent_name, agentProcess);
    } catch (error) {
        console.error(`Error creating agent ${agent_name}:`, error);
        destroyAgent(agent_name);
        return {
            success: false,
            error: error.message
        };
    }
    return {
        success: true,
        error: null
    };
}

export function getAgentProcess(agentName) {
    return getAgentProcessRecord(agentName);
}

export function startAgent(agentName) {
    const process = getAgentProcess(agentName);
    if (process) {
        process.forceRestart();
    }
    else {
        console.error(`Cannot start agent ${agentName}; not found`);
    }
}

export function stopAgent(agentName) {
    const process = getAgentProcess(agentName);
    if (process) {
        process.stop();
    }
    setAgentInGame(agentName, false);
}

export function destroyAgent(agentName) {
    const process = getAgentProcess(agentName);
    if (process) {
        process.stop();
    }
    removeAgent(agentName);
}

export function shutdown() {
    console.log('Shutting down');
    for (const agentName of Object.keys(getAgents())) {
        const process = getAgentProcessRecord(agentName);
        if (process) {
            process.stop();
        }
    }
    setTimeout(() => {
        process.exit(0);
    }, 2000);
}

import { Server } from 'socket.io';
import express from 'express';
import http from 'http';
import path from 'path';
import { fileURLToPath } from 'url';
import * as mindcraft from './mindcraft.js';
import {
    registerAgent as registerAgentRecord,
    getAgent,
    getAgents,
    getAgentsStatus,
    setAgentFullState,
    setAgentInGame,
    setAgentSettings,
    setAgentSocket,
} from './agent_registry.js';
import { readFileSync } from 'fs';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Mindserver is:
// - central hub for communication between all agent processes
// - api to control from other languages and remote users 
// - host for webapp

let io;
let server;
const agent_listeners = [];

const settings_spec = JSON.parse(readFileSync(path.join(__dirname, 'public/settings_spec.json'), 'utf8'));

export async function createAgentFromState(runtime, settings, viewer_port) {
    const agent = runtime.register_agent(settings, viewer_port);
    registerAgentRecord(settings, viewer_port);
    return agent;
}

export function setAgentProcess(agentName, process) {
    const agent = getAgent(agentName);
    if (!agent) return null;
    agent.process = process;
    if (process && process._startOptions) {
        agent.start_options = process._startOptions;
    }
    return agent;
}

export function registerAgent(settings, viewer_port) {
    return registerAgentRecord(settings, viewer_port);
}

export function logoutAgent(agentName) {
    setAgentInGame(agentName, false);
    agentsStatusUpdate();
}

export function getAgentState(agentName) {
    return getAgent(agentName)?.full_state ?? null;
}

export function getAgentStatus(agentName) {
    const agent = getAgent(agentName);
    if (!agent) return null;
    return {
        name: agentName,
        in_game: Boolean(agent.in_game),
        viewerPort: agent.viewer_port,
        socket_connected: Boolean(agent.socket_connected),
    };
}

// Initialize the server
export function createMindServer(host_public = false, port = 8080) {
    const app = express();
    server = http.createServer(app);
    io = new Server(server);

    // Serve static files
    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    app.use(express.static(path.join(__dirname, 'public')));

    // Socket.io connection handling
    io.on('connection', (socket) => {
        let curAgentName = null;
        console.log('Client connected');

        agentsStatusUpdate(socket);

        socket.on('create-agent', async (settings, callback) => {
            console.log('API create agent...');
            for (let key in settings_spec) {
                if (!(key in settings)) {
                    if (settings_spec[key].required) {
                        callback({ success: false, error: `Setting ${key} is required` });
                        return;
                    }
                    else {
                        settings[key] = settings_spec[key].default;
                    }
                }
            }
            for (let key in settings) {
                if (!(key in settings_spec)) {
                    delete settings[key];
                }
            }
            if (settings.profile?.name) {
                if (getAgent(settings.profile.name)) {
                    callback({ success: false, error: 'Agent already exists' });
                    return;
                }
                let returned = await mindcraft.createAgent(settings);
                callback({ success: returned.success, error: returned.error });
                let name = settings.profile.name;
                if (!returned.success && getAgent(name)) {
                    mindcraft.destroyAgent(name);
                }
                agentsStatusUpdate();
            }
            else {
                console.error('Agent name is required in profile');
                callback({ success: false, error: 'Agent name is required in profile' });
            }
        });

        socket.on('get-settings', (agentName, callback) => {
            const agent = getAgent(agentName);
            if (agent) {
                callback({ settings: agent.settings });
            } else {
                callback({ error: `Agent '${agentName}' not found.` });
            }
        });

        socket.on('connect-agent-process', (agentName) => {
            if (getAgent(agentName)) {
                setAgentSocket(agentName, socket);
                agentsStatusUpdate();
            }
        });

        socket.on('login-agent', (agentName) => {
            if (getAgent(agentName)) {
                setAgentSocket(agentName, socket);
                setAgentInGame(agentName, true);
                curAgentName = agentName;
                agentsStatusUpdate();
            }
            else {
                console.warn(`Unregistered agent ${agentName} tried to login`);
            }
        });

        socket.on('disconnect', () => {
            if (getAgent(curAgentName)) {
                console.log(`Agent ${curAgentName} disconnected`);
                setAgentInGame(curAgentName, false);
                setAgentSocket(curAgentName, null);
                agentsStatusUpdate();
            }
            if (agent_listeners.includes(socket)) {
                removeListener(socket);
            }
        });

        socket.on('chat-message', (agentName, json) => {
            if (!getAgent(agentName)) {
                console.warn(`Agent ${agentName} tried to send a message but is not logged in`);
                return;
            }
            console.log(`${curAgentName} sending message to ${agentName}: ${json.message}`);
            getAgent(agentName).socket.emit('chat-message', curAgentName, json);
        });

        socket.on('set-agent-settings', (agentName, settings) => {
            const agent = getAgent(agentName);
            if (agent) {
                setAgentSettings(agentName, settings);
                agent.socket.emit('restart-agent');
            }
        });

        socket.on('restart-agent', (agentName) => {
            console.log(`Restarting agent: ${agentName}`);
            const agent = getAgent(agentName);
            if (agent?.socket) {
                agent.socket.emit('restart-agent');
            }
        });

        socket.on('stop-agent', (agentName) => {
            mindcraft.stopAgent(agentName);
            setAgentInGame(agentName, false);
        });

        socket.on('start-agent', (agentName) => {
            mindcraft.startAgent(agentName);
            setAgentInGame(agentName, true);
        });

        socket.on('destroy-agent', (agentName) => {
            if (getAgent(agentName)) {
                mindcraft.destroyAgent(agentName);
            }
            agentsStatusUpdate();
        });

        socket.on('stop-all-agents', () => {
            console.log('Killing all agents');
            for (let agentName in getAgents()) {
                mindcraft.stopAgent(agentName);
            }
        });

        socket.on('shutdown', () => {
            console.log('Shutting down');
            for (let agentName in getAgents()) {
                mindcraft.stopAgent(agentName);
            }
            // wait 2 seconds
            setTimeout(() => {
                console.log('Exiting MindServer');
                process.exit(0);
            }, 2000);
            
        });

			socket.on('send-message', (agentName, data) => {
				if (!getAgent(agentName)) {
					console.warn(`Agent ${agentName} not in game, cannot send message via MindServer.`);
					return
				}
				try {
					getAgent(agentName).socket.emit('send-message', data)
				} catch (error) {
					console.error('Error: ', error);
				}
			});

        socket.on('bot-output', (agentName, message) => {
            io.emit('bot-output', agentName, message);
        });

        socket.on('run-query-command', (data, callback) => {
            const agentName = data?.agentName;
            const agent = getAgent(agentName);

            if (!agentName || !agent) {
                callback({ success: false, error: `Agent '${agentName}' not found.` });
                return;
            }

            if (!agent.socket) {
                callback({ success: false, error: `Agent '${agentName}' is not connected.` });
                return;
            }

            try {
                agent.socket.emit('run-query-command', data, (response) => {
                    callback(response ?? { success: false, error: 'No response received from agent.' });
                });
            } catch (error) {
                callback({ success: false, error: error.message ?? String(error) });
            }
        });

        socket.on('run-action-command', (data, callback) => {
            const agentName = data?.agentName;
            const agent = getAgent(agentName);

            if (!agentName || !agent) {
                callback({ success: false, error: `Agent '${agentName}' not found.` });
                return;
            }

            if (!agent.socket) {
                callback({ success: false, error: `Agent '${agentName}' is not connected.` });
                return;
            }

            try {
                agent.socket.emit('run-action-command', data, (response) => {
                    callback(response ?? { success: false, error: 'No response received from agent.' });
                });
            } catch (error) {
                callback({ success: false, error: error.message ?? String(error) });
            }
        });

        socket.on('listen-to-agents', () => {
            addListener(socket);
        });
    });

    let host = host_public ? '0.0.0.0' : 'localhost';
    server.listen(port, host, () => {
        console.log(`MindServer running on port ${port}`);
    });

    return server;
}

function agentsStatusUpdate(socket) {
    if (!socket) {
        socket = io;
    }
    let agents = getAgentsStatus();
    socket.emit('agents-status', agents);
}


let listenerInterval = null;
function addListener(listener_socket) {
    agent_listeners.push(listener_socket);
    if (agent_listeners.length === 1) {
        listenerInterval = setInterval(async () => {
            const states = {};
            for (let agentName in getAgents()) {
                let agent = getAgent(agentName);
                if (agent.in_game) {
                    try {
                        const state = await new Promise((resolve) => {
                            agent.socket.emit('get-full-state', (s) => resolve(s));
                        });
                        states[agentName] = state;
                        setAgentFullState(agentName, state);
                    } catch (e) {
                        states[agentName] = { error: String(e) };
                    }
                }
            }
            for (let listener of agent_listeners) {
                listener.emit('state-update', states);
            }
        }, 1000);
    }
}

function removeListener(listener_socket) {
    agent_listeners.splice(agent_listeners.indexOf(listener_socket), 1);
    if (agent_listeners.length === 0) {
        clearInterval(listenerInterval);
        listenerInterval = null;
    }
}

// Optional: export these if you need access to them from other files
export const getIO = () => io;
export const getServer = () => server;
export const numStateListeners = () => agent_listeners.length;

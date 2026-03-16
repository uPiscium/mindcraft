import { io } from 'socket.io-client';

export class MockAgentClient {
    constructor(name, port, settings = {}) {
        this.name = name;
        this.port = port;
        this.settings = settings;
        this.socket = null;
        this.running = false;
        this._startOptions = null;
    }

    async start(load_memory = false, init_message = null, count_id = 0) {
        this._startOptions = { load_memory, init_message, count_id };
        this.running = true;
        this.socket = io(`http://localhost:${this.port}`);

        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error(`Mock agent ${this.name} failed to connect to MindServer`));
            }, 5000);

            this.socket.once('connect', () => {
                clearTimeout(timeout);
                resolve();
            });
            this.socket.once('connect_error', (error) => {
                clearTimeout(timeout);
                reject(error);
            });
        });

        this._registerHandlers();
        await this._login();
    }

    stop() {
        this.running = false;
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    async forceRestart() {
        this.stop();
        if (this._startOptions) {
            await this.start(
                this._startOptions.load_memory,
                this._startOptions.init_message,
                this._startOptions.count_id,
            );
        }
    }

    _registerHandlers() {
        this.socket.on('disconnect', () => {
            this.running = false;
        });

        this.socket.on('restart-agent', async () => {
            await this.forceRestart();
        });

        this.socket.on('get-full-state', (callback) => {
            callback({
                name: this.name,
                mock_client: true,
                actions: {
                    current: 'Idle',
                    isIdle: true,
                },
                stats: {
                    health: 20,
                    hunger: 20,
                    position: { x: 0, y: 64, z: 0 },
                },
            });
        });

        this.socket.on('run-query-command', async (data, callback) => {
            if (!data || data.agentName !== this.name) {
                callback({ success: false, error: 'Query command targeted the wrong mock agent' });
                return;
            }

            try {
                callback({ success: true, result: this._executeQuery(data.message) });
            } catch (error) {
                callback({ success: false, error: error.message ?? String(error) });
            }
        });
    }

    async _login() {
        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error(`Mock agent ${this.name} failed to log in`));
            }, 5000);

            const handleAgentsStatus = (agents) => {
                const current = agents.find((agent) => agent.name === this.name);
                if (current?.in_game && current.socket_connected) {
                    clearTimeout(timeout);
                    this.socket.off('agents-status', handleAgentsStatus);
                    resolve();
                }
            };

            this.socket.on('agents-status', handleAgentsStatus);
            this.socket.emit('connect-agent-process', this.name);
            this.socket.emit('login-agent', this.name);
        });
    }

    _executeQuery(message) {
        if (message.startsWith('!stats')) {
            return [
                'STATS',
                '- Position: x: 0.00, y: 64.00, z: 0.00',
                '- Gamemode: creative',
                '- Health: 20 / 20',
                '- Hunger: 20 / 20',
                '- Biome: plains',
                '- Weather: Clear',
                '- Time: Morning',
                '- Current Action: Idle',
                '- Nearby Human Players: None.',
                '- Nearby Bot Players: None.',
            ].join('\n');
        }

        if (message.startsWith('!inventory')) {
            return 'INVENTORY: Nothing\nWEARING: Nothing';
        }

        if (message.startsWith('!nearbyBlocks')) {
            return 'NEARBY_BLOCKS\n- grass_block\n- First Solid Block Above Head: air';
        }

        if (message.startsWith('!entities')) {
            return 'NEARBY_ENTITIES: none';
        }

        if (message.startsWith('!help')) {
            return 'Mock help is not implemented.';
        }

        throw new Error(`Mock query command not implemented for: ${message}`);
    }
}

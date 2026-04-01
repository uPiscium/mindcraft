import { spawn } from 'child_process';

export class NodeAgentProcess {
    constructor(name, port) {
        this.name = name;
        this.port = port;
        this.process = null;
        this.running = false;
        this._startOptions = null;
    }

    async start(load_memory = false, init_message = null, count_id = 0, profile_path = null) {
        this._startOptions = { load_memory, init_message, count_id, profile_path };
        this.running = true;

        const nodeBinary = process.env.NODE_BINARY || 'node';
        const args = [
            'src/process/init_agent.js',
            this.name,
            '-n',
            this.name,
            '-c',
            String(count_id),
            '-p',
            String(this.port),
        ];

        if (load_memory) {
            args.push('-l', String(load_memory));
        }
        if (init_message) {
            args.push('-m', init_message);
        }

        this.process = spawn(nodeBinary, args, {
            stdio: 'inherit',
            stderr: 'inherit',
        });

        this.process.on('exit', (code, signal) => {
            this.running = false;
            if (code !== 0 && signal !== 'SIGINT') {
                console.log(`Agent ${this.name} exited with code ${code} and signal ${signal}`);
            }
        });

        this.process.on('error', (err) => {
            console.error('Agent process error:', err);
        });

        return this.process;
    }

    stop() {
        if (!this.running || !this.process) {
            return;
        }
        this.process.kill('SIGINT');
    }

    async forceRestart() {
        this.stop();
        if (this._startOptions) {
            await this.start(
                this._startOptions.load_memory,
                this._startOptions.init_message,
                this._startOptions.count_id,
                this._startOptions.profile_path,
            );
        }
    }
}

import { spawn, ChildProcess } from 'child_process';
import { logoutAgent } from '../mindcraft/mindserver';

export class AgentProcess {
  name: string;
  port: number;
  process: ChildProcess | null = null;
  running: boolean = false;
  count_id: number = 0;

  constructor(name: string, port: number) {
    this.name = name;
    this.port = port;
  }

  start(load_memory: boolean = false, init_message: string | null = null, count_id: number = 0): void {
    this.count_id = count_id;
    this.running = true;

    let args = ['src/process/init_agent.js', this.name];
    args.push('-n', this.name);
    args.push('-c', String(count_id));
    if (load_memory)
      args.push('-l', String(load_memory));
    if (init_message)
      args.push('-m', init_message);
    args.push('-p', String(this.port));

    const agentProcess = spawn('node', args, {
      stdio: 'inherit',
    });

    let last_restart = Date.now();
    agentProcess.on('exit', (code: number, signal: string) => {
      console.log(`Agent process exited with code ${code} and signal ${signal}`);
      this.running = false;
      logoutAgent(this.name);

      if (code > 1) {
        console.log(`Ending task`);
        process.exit(code);
      }

      if (code !== 0 && signal !== 'SIGINT') {
        // agent must run for at least 10 seconds before restarting
        if (Date.now() - last_restart < 10000) {
          console.error(`Agent process exited too quickly and will not be restarted.`);
          return;
        }
        console.log('Restarting agent...');
        this.start(true, 'Agent process restarted.', count_id);
        last_restart = Date.now();
      }
    });

    agentProcess.on('error', (err) => {
      console.error('Agent process error:', err);
    });

    this.process = agentProcess;
  }

  stop() {
    if (!this.running) return;
    this.process?.kill('SIGINT');
  }

  forceRestart() {
    if (this.running && this.process && !this.process.killed) {
      console.log(`Agent process for ${this.name} is still running. Attempting to force restart.`);

      const restartTimeout = setTimeout(() => {
        console.warn(`Agent ${this.name} did not stop in time. It might be stuck.`);
      }, 5000); // 5 seconds to exit

      this.process.once('exit', () => {
        clearTimeout(restartTimeout);
        console.log(`Stopped hanging agent ${this.name}. Now restarting.`);
        this.start(true, 'Agent process restarted.', this.count_id);
      });
      this.stop(); // sends SIGINT
    } else {
      this.start(true, 'Agent process restarted.', this.count_id);
    }
  }
}

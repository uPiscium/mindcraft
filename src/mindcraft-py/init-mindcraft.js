import * as Mindcraft from '../mindcraft/mindcraft.js';
import settings from '../../settings.js';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

function parseArguments() {
    return yargs(hideBin(process.argv))
        .option('mindserver_port', {
            type: 'number',
            describe: 'Mindserver port',
            default: settings.mindserver_port
        })
        .option('host_public', {
            type: 'boolean',
            describe: 'Bind MindServer to all interfaces',
            default: true
        })
        .option('auto_open_ui', {
            type: 'boolean',
            describe: 'Automatically open UI in browser',
            default: settings.auto_open_ui
        })
        .help()
        .alias('help', 'h')
        .parse();
}

const args = parseArguments();

settings.mindserver_port = args.mindserver_port;
settings.auto_open_ui = args.auto_open_ui;

Mindcraft.init(args.host_public, settings.mindserver_port, settings.auto_open_ui);

console.log(`Mindcraft initialized with MindServer at localhost:${settings.mindserver_port}`);

import process from 'node:process';
import * as Mindcraft from './src/mindcraft/mindcraft.js';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import { readFileSync } from 'node:fs';
import { bootstrapApp } from './src/bootstrap/bootstrap.js';
import { loadSettings } from './src/config/settings.js';

const context = bootstrapApp({
    baseSettings: loadSettings({}),
    argv: process.argv,
    env: process.env,
    yargsFactory: yargs,
    hideBin,
    readTaskFile: readFileSync,
});

Mindcraft.init(true, context.mindserverPort, context.autoOpenUi);

for (const profile of context.profiles) {
    const profileJson = JSON.parse(readFileSync(profile, 'utf8'));
    context.settings.profile = profileJson;
    Mindcraft.createAgent(context.settings);
}

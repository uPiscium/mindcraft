import { strict as assert } from 'assert';
import { test } from 'node:test';
import { SelfPrompter } from '../src/agent/self_prompter.js';

test('self prompter starts with task context and prompt injection', async () => {
    const agent = {
        handleMessage: async () => false,
        openChat: () => {},
        actions: { stop: async () => {} },
        isIdle: () => true,
    };

    const prompter = new SelfPrompter(agent);
    let loopStarted = 0;
    prompter.startLoop = async () => {
        loopStarted += 1;
    };

    prompter.setTaskContext({ goal: 'Collect logs' });
    prompter.start('Base prompt');

    assert.equal(prompter.isActive(), true);
    assert.match(prompter.prompt, /Base prompt/);
    assert.match(prompter.prompt, /CURRENT TASK:\nCollect logs/);
    assert.equal(loopStarted, 1);
});

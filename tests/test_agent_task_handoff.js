import { strict as assert } from 'assert';
import { test } from 'node:test';
import { Agent } from '../src/agent/agent.js';

test('agent activates the next task after completion', async () => {
    const nextTask = { id: 'craft_planks', goal: 'Craft planks', payload: 'Craft planks' };
    const completedTask = { id: 'gather_oak_logs', goal: 'Collect logs', payload: 'Collect logs' };
    const activated = [];

    const agent = Object.create(Agent.prototype);
    agent.name = 'Andy';
    agent.task = { current_task: completedTask };
    agent.self_prompter = {
        active: false,
        clearTaskContext() {
            this.active = false;
        },
        setTaskContext(task) {
            this.task = task;
        },
        isActive() {
            return this.active;
        },
        start(prompt) {
            this.active = true;
            this.prompt = prompt;
        },
    };
    agent.task_pool = {
        isDrivingTask() {
            return true;
        },
        completeCurrentTask(reason) {
            activated.push(['complete', reason]);
            return completedTask;
        },
        hasAvailableTask() {
            return true;
        },
        acquireNextTask() {
            activated.push(['acquire']);
            return nextTask;
        },
    };
    agent._activateTask = async (task) => {
        activated.push(['activate', task.id]);
        agent.self_prompter.setTaskContext(task);
        agent.self_prompter.start(task.goal || task.payload || task.id);
        return task;
    };

    await agent.onActionSucceeded('mine', { success: true });

    assert.deepEqual(activated, [
        ['complete', 'mine completed'],
        ['acquire'],
        ['activate', 'craft_planks'],
    ]);
    assert.equal(agent.task.current_task, null);
    assert.equal(agent.self_prompter.task.id, 'craft_planks');
    assert.equal(agent.self_prompter.prompt, 'Craft planks');
});

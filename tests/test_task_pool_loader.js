import { TaskPool } from '../src/agent/tasks/task_pool.js';

test('task pool acquires tasks in dependency order', () => {
    const pool = new TaskPool([
        { id: 'gather_oak_logs', payload: 'Collect logs', priority: 1 },
        { id: 'craft_planks', payload: 'Craft planks', depends_on: ['gather_oak_logs'], priority: 2 },
    ]);

    const first = pool.acquireNextTask();
    expect(first.id).toBe('gather_oak_logs');
    expect(pool.getCurrentTaskState()).toBe('LOCKED');

    pool.completeCurrentTask('done');
    const second = pool.acquireNextTask();
    expect(second.id).toBe('craft_planks');
});

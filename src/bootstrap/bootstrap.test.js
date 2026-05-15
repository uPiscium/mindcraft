import test from 'node:test';
import assert from 'node:assert/strict';

import {
  createBootstrapContext,
  resolveBootstrapSettings,
  validateBootstrapSettings,
} from './bootstrap.js';

test('resolveBootstrapSettings merges env and cli input', () => {
  const result = resolveBootstrapSettings(
    { profiles: ['base.json'], mindserver_port: 8080, auto_open_ui: true },
    { profiles: ['cli.json'] },
    { MINDSERVER_PORT: '9090', LOG_ALL: 'true' },
    () => '{"ignored":true}'
  );

  assert.equal(result.profiles[0], 'cli.json');
  assert.equal(result.mindserver_port, 9090);
  assert.equal(result.log_all_prompts, true);
});

test('resolveBootstrapSettings loads task by task id', () => {
  const result = resolveBootstrapSettings(
    { profiles: ['base.json'] },
    { task_path: '/tmp/tasks.json', task_id: 'gather' },
    {},
    () => '{"gather":{"goal":"collect"}}'
  );

  assert.equal(result.task.task_id, 'gather');
  assert.equal(result.task.goal, 'collect');
});

test('validateBootstrapSettings rejects missing profiles', () => {
  assert.throws(() => validateBootstrapSettings({ profiles: [] }), /profiles/);
});

test('createBootstrapContext returns downstream context', () => {
  const context = createBootstrapContext({
    profiles: ['a.json'],
    mindserver_port: 8080,
    auto_open_ui: false,
  });

  assert.equal(context.mindserverPort, 8080);
  assert.equal(context.autoOpenUi, false);
  assert.deepEqual(context.profiles, ['a.json']);
});

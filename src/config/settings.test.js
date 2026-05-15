import test from 'node:test';
import assert from 'node:assert/strict';
import { loadSettings } from './settings.js';
import { normalizeModelDescriptor } from './model.js';

test('loadSettings keeps valid settings and applies env overrides', () => {
  const settings = loadSettings({ MINDSERVER_PORT: '9090', MAX_MESSAGES: '20' });
  assert.equal(settings.mindserver_port, 9090);
  assert.equal(settings.max_messages, 20);
});

test('normalizeModelDescriptor resolves string model hints', () => {
  assert.deepEqual(normalizeModelDescriptor('gpt-4o-mini'), { api: 'openai', model: 'gpt-4o-mini' });
});

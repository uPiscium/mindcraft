import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeModelDescriptor } from './model.js';

test('normalizeModelDescriptor resolves string models', () => {
  assert.deepEqual(normalizeModelDescriptor('gpt-4o-mini'), { api: 'openai', model: 'gpt-4o-mini' });
});

test('normalizeModelDescriptor resolves object models', () => {
  assert.deepEqual(
    normalizeModelDescriptor({ api: 'azure', model: 'azure/gpt-4o', url: 'https://example', params: { apiVersion: '1' } }),
    { api: 'azure', model: 'gpt-4o', url: 'https://example', params: { apiVersion: '1' } }
  );
});

test('normalizeModelDescriptor rejects unknown model', () => {
  assert.throws(() => normalizeModelDescriptor({ model: 'unknown-model' }), /Unknown model/);
});

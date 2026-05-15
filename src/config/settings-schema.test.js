import test from 'node:test';
import assert from 'node:assert/strict';
import { validateSettings } from './settings-schema.js';

test('validateSettings fills defaults', () => {
  const settings = validateSettings({ profiles: ['a.json'] });
  assert.equal(settings.port, 40000);
  assert.equal(settings.auth, 'offline');
});

test('validateSettings rejects invalid types', () => {
  assert.throws(() => validateSettings({ profiles: 'bad' }), /must be of type array/);
});

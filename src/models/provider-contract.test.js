import test from 'node:test';
import assert from 'node:assert/strict';
import { GPT } from './gpt.js';
import { Claude } from './claude.js';

test('GPT exposes chat alongside sendRequest', () => {
  const model = Object.create(GPT.prototype);
  model.sendRequest = () => Promise.resolve('ok');
  return model.chat([], 'system').then((result) => {
    assert.equal(result, 'ok');
  });
});

test('Claude exposes chat alongside sendRequest', () => {
  const model = Object.create(Claude.prototype);
  model.sendRequest = () => Promise.resolve('ok');
  return model.chat([], 'system').then((result) => {
    assert.equal(result, 'ok');
  });
});

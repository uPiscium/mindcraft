import { strict as assert } from 'assert';
import { Ollama } from '../src/models/ollama.js';

class TestOllama extends Ollama {
    constructor(...args) {
        super(...args);
        this.sentBodies = [];
    }

    async send(endpoint, body) {
        this.sentBodies.push({ endpoint, body });
        return { message: { content: 'hello <think>skip</think> world' } };
    }
}

async function main() {
    const client = new TestOllama('test-model', 'http://localhost:11434', { temperature: 0.2 });

    const result = await client.sendRequest([{ role: 'user', content: 'hi' }], 'system');

    assert.equal(result, 'hello  world');
    assert.equal(client.sentBodies.length, 1);
    assert.equal(client.sentBodies[0].body.options.num_ctx, 4096);
    assert.equal(client.sentBodies[0].body.temperature, 0.2);
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});

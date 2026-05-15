const COMMON_MODEL_HINTS = [
  ['gpt', 'openai'],
  ['o1', 'openai'],
  ['o3', 'openai'],
  ['claude', 'anthropic'],
  ['gemini', 'google'],
  ['grok', 'xai'],
  ['mistral', 'mistral'],
  ['deepseek', 'deepseek'],
  ['qwen', 'qwen'],
];

export function normalizeModelDescriptor(input) {
  if (typeof input === 'string' || input instanceof String) {
    return normalizeModelDescriptor({ model: String(input) });
  }

  const descriptor = {
    api: input.api ?? '',
    model: input.model ?? null,
  };

  if (input.url !== undefined) {
    descriptor.url = input.url;
  }
  if (input.params !== undefined) {
    descriptor.params = input.params;
  }

  if (descriptor.model?.includes('local')) {
    descriptor.api = 'ollama';
    descriptor.model = descriptor.model.replace('local', 'ollama');
  }

  if (!descriptor.api) {
    if (descriptor.model) {
      const slashIndex = descriptor.model.indexOf('/');
      if (slashIndex > 0) {
        descriptor.api = descriptor.model.slice(0, slashIndex);
      }
    }

    if (!descriptor.api && descriptor.model) {
      for (const [hint, api] of COMMON_MODEL_HINTS) {
        if (descriptor.model.includes(hint)) {
          descriptor.api = api;
          break;
        }
      }
    }
  }

  if (!descriptor.api) {
    throw new Error(`Unknown model: ${descriptor.model ?? 'undefined'}`);
  }

  const apiPrefix = `${descriptor.api}/`;
  if (descriptor.model?.startsWith(apiPrefix)) {
    descriptor.model = descriptor.model.slice(apiPrefix.length) || null;
  }

  return descriptor;
}

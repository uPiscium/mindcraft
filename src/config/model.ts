export type ModelDescriptorInput = string | {
  api?: string;
  model?: string | null;
  url?: string;
  params?: Record<string, unknown>;
};

export type NormalizedModelDescriptor = {
  api: string;
  model: string | null;
  url?: string | undefined;
  params?: Record<string, unknown> | undefined;
};

const COMMON_MODEL_HINTS: Array<[string, string]> = [
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

export function normalizeModelDescriptor(input: ModelDescriptorInput): NormalizedModelDescriptor {
  if (typeof input === 'string' || input instanceof String) {
    return normalizeModelDescriptor({ model: String(input) });
  }

  const descriptor: NormalizedModelDescriptor = {
    api: input.api ?? '',
    model: input.model ?? null,
    url: input.url,
    params: input.params,
  };

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

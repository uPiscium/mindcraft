import { Claude } from '../models/claude.js';
import { GPT } from '../models/gpt.js';
import { Gemini } from '../models/gemini.js';
import { GroqCloudAPI } from '../models/groq.js';
import { DeepSeek } from '../models/deepseek.js';
import { Qwen } from '../models/qwen.js';
import { Mistral } from '../models/mistral.js';
import { Ollama } from '../models/ollama.js';
import { ReplicateAPI } from '../models/replicate.js';
import { Cerebras } from '../models/cerebras.js';
import { Mercury } from '../models/mercury.js';
import { OpenRouter } from '../models/openrouter.js';
import { VLLM } from '../models/vllm.js';
import { Hyperbolic } from '../models/hyperbolic.js';
import { GLHF } from '../models/glhf.js';
import { HuggingFace } from '../models/huggingface.js';
import { Novita } from '../models/novita.js';
import { Grok } from '../models/grok.js';
import { AzureGPT } from '../models/azure.js';

export const providerRegistry = {
  anthropic: Claude,
  openai: GPT,
  google: Gemini,
  groq: GroqCloudAPI,
  deepseek: DeepSeek,
  qwen: Qwen,
  mistral: Mistral,
  ollama: Ollama,
  replicate: ReplicateAPI,
  cerebras: Cerebras,
  mercury: Mercury,
  openrouter: OpenRouter,
  vllm: VLLM,
  hyperbolic: Hyperbolic,
  glhf: GLHF,
  huggingface: HuggingFace,
  novita: Novita,
  xai: Grok,
  azure: AzureGPT,
};

export function resolveProvider(api) {
  const provider = providerRegistry[api];
  if (!provider) {
    throw new Error(`Unknown api: ${api}`);
  }
  return provider;
}

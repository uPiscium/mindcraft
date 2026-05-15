const primitive = (type, defaultValue) => ({ type, default: defaultValue });

export const settingsSchema = {
  minecraft_version: primitive('string', 'auto'),
  host: primitive('string', '10.12.1.100'),
  port: primitive('number', 40000),
  auth: { type: 'string', default: 'offline', options: ['offline', 'microsoft'] },
  mindserver_port: primitive('number', 8080),
  auto_open_ui: primitive('boolean', true),
  base_profile: primitive('string', 'assistant'),
  profiles: { type: 'array', default: ['./agents/Andy.json', './agents/Bob.json', './agents/Clara.json'] },
  profile: { type: 'object', required: false, default: {} },
  load_memory: primitive('boolean', false),
  init_message: primitive('string', 'Respond with hello world and your name'),
  only_chat_with: { type: 'array', default: [] },
  speak: primitive('boolean', false),
  chat_ingame: primitive('boolean', true),
  language: primitive('string', 'en'),
  render_bot_view: primitive('boolean', false),
  allow_insecure_coding: primitive('boolean', true),
  allow_vision: primitive('boolean', false),
  blocked_actions: { type: 'array', default: ['!checkBlueprint', '!checkBlueprintLevel', '!getBlueprint', '!getBlueprintLevel'] },
  code_timeout_mins: primitive('number', -1),
  relevant_docs_count: primitive('number', 5),
  max_messages: primitive('number', 15),
  num_examples: primitive('number', 2),
  max_commands: primitive('number', -1),
  show_command_syntax: { type: 'string', default: 'full', options: ['full', 'shortened', 'none'] },
  narrate_behavior: primitive('boolean', true),
  chat_bot_messages: primitive('boolean', true),
  spawn_timeout: primitive('number', 30),
  block_place_delay: primitive('number', 0),
  log_all_prompts: primitive('boolean', false),
  task: { type: 'object', required: false, default: null },
};

const NUMERIC_ENV_KEYS = new Set(['MINECRAFT_PORT', 'MINDSERVER_PORT', 'MAX_MESSAGES', 'NUM_EXAMPLES', 'LOG_ALL']);

export function parseSettingsValue(key, value) {
  const spec = settingsSchema[key];
  if (!spec) {
    return value;
  }

  if (spec.type === 'number' && typeof value === 'string') {
    const parsed = Number(value);
    return Number.isNaN(parsed) ? value : parsed;
  }
  if (spec.type === 'boolean' && typeof value === 'string') {
    return value === 'true';
  }
  if (spec.type === 'array' && typeof value === 'string') {
    return JSON.parse(value);
  }
  if (spec.type === 'object' && typeof value === 'string') {
    return JSON.parse(value);
  }
  return value;
}

export function validateSettings(settings) {
  for (const [key, spec] of Object.entries(settingsSchema)) {
    if (spec.required && settings[key] === undefined) {
      throw new Error(`Setting ${key} is required`);
    }
    if (settings[key] === undefined) {
      settings[key] = spec.default;
    }

    const value = settings[key];
    if (value === undefined || value === null) {
      continue;
    }

    const validType =
      (spec.type === 'string' && typeof value === 'string') ||
      (spec.type === 'number' && typeof value === 'number' && Number.isFinite(value)) ||
      (spec.type === 'boolean' && typeof value === 'boolean') ||
      (spec.type === 'array' && Array.isArray(value)) ||
      (spec.type === 'object' && typeof value === 'object' && !Array.isArray(value));

    if (!validType) {
      throw new Error(`Setting ${key} must be of type ${spec.type}`);
    }

    if (spec.options && typeof value === 'string' && !spec.options.includes(value)) {
      throw new Error(`Setting ${key} must be one of: ${spec.options.join(', ')}`);
    }
  }

  for (const key of Object.keys(settings)) {
    if (!(key in settingsSchema)) {
      delete settings[key];
    }
  }

  return settings;
}

export function applyEnvOverrides(settings, env) {
  if (env.MINECRAFT_PORT) settings.port = parseSettingsValue('port', env.MINECRAFT_PORT);
  if (env.MINDSERVER_PORT) settings.mindserver_port = parseSettingsValue('mindserver_port', env.MINDSERVER_PORT);
  if (env.PROFILES) settings.profiles = parseSettingsValue('profiles', env.PROFILES);
  if (env.INSECURE_CODING) settings.allow_insecure_coding = true;
  if (env.BLOCKED_ACTIONS) settings.blocked_actions = parseSettingsValue('blocked_actions', env.BLOCKED_ACTIONS);
  if (env.MAX_MESSAGES) settings.max_messages = parseSettingsValue('max_messages', env.MAX_MESSAGES);
  if (env.NUM_EXAMPLES) settings.num_examples = parseSettingsValue('num_examples', env.NUM_EXAMPLES);
  if (env.LOG_ALL) settings.log_all_prompts = parseSettingsValue('log_all_prompts', env.LOG_ALL);
  return settings;
}

import { readFileSync } from 'node:fs';

export function parseArguments(argv, yargsFactory, hideBin) {
  return yargsFactory(hideBin(argv))
    .option('profiles', {
      type: 'array',
      describe: 'List of agent profile paths',
    })
    .option('task_path', {
      type: 'string',
      describe: 'Path to task file to execute',
    })
    .option('task_id', {
      type: 'string',
      describe: 'Task ID to execute',
    })
    .help()
    .alias('help', 'h')
    .parse();
}

export function resolveBootstrapSettings(baseSettings, args, env, readTaskFile = readFileSync) {
  const settings = structuredClone(baseSettings);

  if (args.profiles?.length) {
    settings.profiles = args.profiles;
  }

  if (args.task_path) {
    if (!args.task_id) {
      throw new Error('task_id is required when task_path is provided');
    }

    const tasks = JSON.parse(readTaskFile(args.task_path, 'utf8'));
    settings.task = tasks[args.task_id];
    if (!settings.task) {
      throw new Error(`Task '${args.task_id}' not found in ${args.task_path}`);
    }
    settings.task.task_id = args.task_id;
  }

  if (env.MINECRAFT_PORT) {
    settings.port = env.MINECRAFT_PORT;
  }
  if (env.MINDSERVER_PORT) {
    settings.mindserver_port = env.MINDSERVER_PORT;
  }
  if (env.PROFILES && JSON.parse(env.PROFILES).length > 0) {
    settings.profiles = JSON.parse(env.PROFILES);
  }
  if (env.INSECURE_CODING) {
    settings.allow_insecure_coding = true;
  }
  if (env.BLOCKED_ACTIONS) {
    settings.blocked_actions = JSON.parse(env.BLOCKED_ACTIONS);
  }
  if (env.MAX_MESSAGES) {
    settings.max_messages = env.MAX_MESSAGES;
  }
  if (env.NUM_EXAMPLES) {
    settings.num_examples = env.NUM_EXAMPLES;
  }
  if (env.LOG_ALL) {
    settings.log_all_prompts = env.LOG_ALL;
  }

  return settings;
}

export function validateBootstrapSettings(settings) {
  const missing = [];

  if (!settings.profiles || settings.profiles.length === 0) {
    missing.push('profiles');
  }
  if (!settings.task_path && settings.task && !settings.task.task_id) {
    missing.push('task_id');
  }

  if (missing.length > 0) {
    throw new Error(`Missing required bootstrap setting(s): ${missing.join(', ')}`);
  }

  return settings;
}

export function createBootstrapContext(settings) {
  return {
    mindserverPort: settings.mindserver_port,
    autoOpenUi: settings.auto_open_ui,
    profiles: settings.profiles ?? [],
    settings,
  };
}

export function bootstrapApp({
  baseSettings,
  argv,
  env,
  yargsFactory,
  hideBin,
  readTaskFile = readFileSync,
}) {
  const args = parseArguments(argv, yargsFactory, hideBin);
  const settings = resolveBootstrapSettings(baseSettings, args, env, readTaskFile);
  validateBootstrapSettings(settings);
  return createBootstrapContext(settings);
}

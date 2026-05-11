import { History } from './history';
import { Coder } from './coder';
import { VisionInterpreter } from './vision/vision_interpreter';
import { Prompter } from '../models/prompter';
import { initModes } from './modes';
import { initBot } from '../utils/mcdata';
import { containsCommand, commandExists, executeCommand, truncCommandMessage, isAction, blacklistCommands } from './commands/index';
import { ActionManager } from './action_manager';
import { NPCContoller } from './npc/controller';
import { MemoryBank } from './memory_bank';
import { SelfPrompter } from './self_prompter';
import convoManager from './conversation';
import { handleTranslation, handleEnglishTranslation } from '../utils/translator';
import { addBrowserViewer } from './vision/browser_viewer';
import { serverProxy, sendOutputToServer } from './mindserver_proxy';
import settings from './settings';
import { Task } from './tasks/tasks';
// import { speak } from './speak.js';
import { log, validateNameFormat, handleDisconnection } from './connection_handler';

type BotError = Error & { code?: string };

type ErrorLike = {
  message: string;
  code?: string;
};

type ConversationManager = {
  isOtherAgent(name: string): boolean;
  inConversation(name: string): boolean;
  responseScheduledFor(name: string): boolean;
  sendToBot(name: string, message: string): void;
  otherAgentInGame(name: string): boolean;
  receiveFromBot(name: string, message: { message: string; start: boolean }): void;
  endAllConversations(): void;
  initAgent(agent: Agent): void;
};

const convo = convoManager as unknown as ConversationManager;

interface AgentBot {
  once(event: string, listener: ((...args: unknown[]) => void) | ((reason: string) => void)): void;
  on(event: string, listener: ((...args: unknown[]) => void) | ((reason: string, message?: string) => void)): void;
  emit(event: string, ...args: unknown[]): void;
  chat(message: string): void;
  whisper(username: string, message: string): void;
  stopDigging(): void;
  clearControlStates(): void;
  pathfinder: { stop(): void };
  collectBlock: { cancelTask(): void };
  pvp: { stop(): void };
  autoEat: { options?: { priority?: string; startAt?: number; bannedFood?: string[] } };
  modes: { flushBehaviorLog(): string; update(): Promise<void>; unPauseAll(): void; pause(mode: string): void; unPauseAll(): void };
  entity: { position: { x: number; y: number; z: number }; height: number; yaw: number; pitch: number };
  time: { timeOfDay: number };
  health: number;
  lastDamageTime: number;
  lastDamageTaken: number;
  game: { dimension: string };
  output: string;
  interrupt_code: boolean;
  players: Record<string, unknown>;
  world?: unknown;
  profile?: { skin?: { model: string; path: string } };
  [key: string]: unknown;
}

const appSettings = settings as {
  profile: { skin?: { model: string; path: string } };
  task: string;
  blocked_actions: string[];
  spawn_timeout: number;
  allow_vision: boolean;
  only_chat_with: string[];
  max_commands: number;
  show_command_syntax: 'full' | 'shortened' | 'off';
  chat_ingame: boolean;
};

function isBotError(err: unknown): err is BotError {
  return err instanceof Error;
}

function hasErrorMessage(err: unknown): err is ErrorLike {
  return typeof err === 'object' && err !== null && 'message' in err && typeof (err as { message?: unknown }).message === 'string';
}

export class Agent {
  last_sender: string | null = null;
  count_id: number = 0;
  _disconnectHandled: boolean = false;

  actions!: ActionManager;
  prompter!: Prompter;
  name: string = '';
  history!: History;
  coder!: Coder;
  npc!: NPCContoller;
  memory_bank!: MemoryBank;
  self_prompter!: SelfPrompter;
  task: Task | null = null;
  blocked_actions: string[] = [];
  bot: AgentBot | null = null;
  vision_interpreter!: VisionInterpreter;
  shut_up: boolean = false;
  respondFunc!: (username: string, message: string) => Promise<void>;

  async start(load_mem = false, init_message: string | null = null, count_id = 0) {
    this.last_sender = null;
    this.count_id = count_id;
    this._disconnectHandled = false;

    // Initialize components
    this.actions = new ActionManager(this);
    this.prompter = new Prompter(this, appSettings.profile);
    this.name = (this.prompter.getName() || '').trim();
    console.log(`Initializing agent ${this.name}...`);

    // Validate Name Format
    // connection_handler now ensures the message has [LoginGuard] prefix
    const nameCheck = validateNameFormat(this.name);
    if (!nameCheck.success) {
      log(this.name, nameCheck.msg);
      process.exit(1);
      // return;
    }

    this.history = new History(this);
    this.coder = new Coder(this);
    this.npc = new NPCContoller(this);
    this.memory_bank = new MemoryBank();
    this.self_prompter = new SelfPrompter(this);
    convoManager.initAgent(this);
    await this.prompter.initExamples();

    // load mem first before doing task
    let save_data = null;
    if (load_mem) {
      save_data = this.history.load();
    }
    let taskStart: number | null = null;
    if (save_data) {
      taskStart = save_data.taskStart;
    } else {
      taskStart = Date.now();
    }
    this.task = new Task(this, appSettings.task, taskStart ?? undefined);
    this.blocked_actions = appSettings.blocked_actions.concat(this.task.blocked_actions || []);
    blacklistCommands(this.blocked_actions);

    console.log(this.name, 'logging into minecraft...');
    this.bot = initBot(this.name) as unknown as AgentBot;

    // Connection Handler
    const onDisconnect = (_event: string | undefined, reason: string) => {
      if (this._disconnectHandled) return;
      this._disconnectHandled = true;

      // Log and Analyze
      // handleDisconnection handles logging to console and server
      // TODO: Analyze `type` infomation
      const { type } = handleDisconnection(this.name, reason);

      process.exit(1);
    };

    // Bind events
    const bot = this.bot;
    if (!bot) throw new Error('Bot failed to initialize');

    bot.once('kicked', ((reason: unknown) => onDisconnect('Kicked', String(reason))) as (...args: unknown[]) => void);
    bot.once('end', ((reason: unknown) => onDisconnect('Disconnected', String(reason))) as (...args: unknown[]) => void);
    bot.on('error', (err: unknown) => {
      if (hasErrorMessage(err)) {
        const message = err.message;
        const code = err.code;
        if (message.includes('Duplicate') || code === 'ECONNREFUSED') {
          onDisconnect('Error', message);
        } else {
          log(this.name, `[LoginGuard] Connection Error: ${message}`);
        }
      } else {
        log(this.name, '[LoginGuard] Connection Error: unknown error');
      }
    });

    initModes(this);

    bot.on('login', (() => {
      console.log(this.name, 'logged in!');
      serverProxy.login();

      // Set skin for profile, requires Fabric Tailor. (https://modrinth.com/mod/fabrictailor)
        if (this.prompter.profile.skin)
          bot.chat(`/skin set URL ${this.prompter.profile.skin.model} ${this.prompter.profile.skin.path}`);
        else
          bot.chat(`/skin clear`);
    }) as (...args: unknown[]) => void);
    const spawnTimeoutDuration = appSettings.spawn_timeout;
    const spawnTimeout = setTimeout(() => {
      const msg = `Bot has not spawned after ${spawnTimeoutDuration} seconds. Exiting.`;
      log(this.name, msg);
      process.exit(1);
    }, spawnTimeoutDuration * 1000);
    bot.once('spawn', (async () => {
      try {
        clearTimeout(spawnTimeout);
        addBrowserViewer(bot, count_id);
        console.log('Initializing vision intepreter...');
        this.vision_interpreter = new VisionInterpreter(this, appSettings.allow_vision);

        // wait for a bit so stats are not undefined
        await new Promise((resolve) => setTimeout(resolve, 1000));

        console.log(`${this.name} spawned.`);
        this.clearBotLogs();

        this._setupEventHandlers(save_data, init_message);
        this.startEvents();

        if (!load_mem) {
          if (appSettings.task) {
            if (this.task === null) {
              console.error('Task is null after initialization');
              process.exit(1);
            }
            this.task.initBotTask();
            this.task.setAgentGoal();
          }
        } else {
          // set the goal without initializing the rest of the task
          if (appSettings.task) {
            if (this.task === null) {
              console.error('Task is null after initialization');
              process.exit(1);
            }
            this.task.setAgentGoal();
          }
        }

        await new Promise((resolve) => setTimeout(resolve, 10000));
        this.checkAllPlayersPresent();

      } catch (error) {
        console.error('Error in spawn event:', error);
        process.exit(0);
      }
    }) as (...args: unknown[]) => void);
  }

  async _setupEventHandlers(save_data: { self_prompt?: string | null; self_prompting_state?: unknown; last_sender?: string } | null, init_message: string | null) {
    const ignore_messages = [
      "Set own game mode to",
      "Set the time to",
      "Set the difficulty to",
      "Teleported ",
      "Set the weather to",
      "Gamerule "
    ];

    const respondFunc = async (username: string, message: string) => {
      if (message === "") return;
      if (username === this.name) return;
      if (appSettings.only_chat_with.length > 0 && !appSettings.only_chat_with.includes(username)) return;
      try {
        if (ignore_messages.some((m) => message.startsWith(m))) return;

        this.shut_up = false;

        console.log(this.name, 'received message from', username, ':', message);

        if (convoManager.isOtherAgent(username)) {
          console.warn('received whisper from other bot??');
        }
        else {
          let translation = await handleEnglishTranslation(message);
          this.handleMessage(username, translation);
        }
      } catch (error) {
        console.error('Error handling message:', error);
      }
    };

    this.respondFunc = respondFunc;

    const bot = this.bot;
    if (!bot) throw new Error('Bot is not initialized');

    bot.on('whisper', ((...args: unknown[]) => {
      const [username, message] = args as [string, string];
      void respondFunc(username, message);
    }) as (...args: unknown[]) => void);

    bot.on('chat', ((...args: unknown[]) => {
      const [username, message] = args as [string, string];
      if (serverProxy.getNumOtherAgents() > 0) return;
      // only respond to open chat messages when there are no other agents
      respondFunc(username, message);
    }) as (...args: unknown[]) => void);

    // Set up auto-eat
    bot.autoEat.options = {
      priority: 'foodPoints',
      startAt: 14,
      bannedFood: ["rotten_flesh", "spider_eye", "poisonous_potato", "pufferfish", "chicken"]
    };

    if (save_data?.self_prompt) {
      if (init_message) {
        this.history.add('system', init_message);
      }
      await this.self_prompter.handleLoad(save_data.self_prompt, save_data.self_prompting_state);
    }
    if (save_data?.last_sender) {
      this.last_sender = save_data.last_sender;
      if (convoManager.otherAgentInGame(this.last_sender)) {
        const msg_package = {
          message: `You have restarted and this message is auto-generated. Continue the conversation with me.`,
          start: true
        };
        convoManager.receiveFromBot(this.last_sender, msg_package);
      }
    }
    else if (init_message) {
      await this.handleMessage('system', init_message, 2);
    }
    else {
      this.openChat("Hello world! I am " + this.name);
    }
  }

  checkAllPlayersPresent() {
    if (!this.task || !this.task.agent_names) {
      return;
    }

    const missingPlayers = this.task.agent_names.filter(name => !this.bot?.players?.[name]);
    if (missingPlayers.length > 0) {
      console.log(`Missing players/bots: ${missingPlayers.join(', ')}`);
      this.cleanKill('Not all required players/bots are present in the world. Exiting.', 4);
    }
  }

  requestInterrupt() {
    const bot = this.bot;
    if (!bot) return;
    bot.interrupt_code = true;
    bot.stopDigging();
    bot.collectBlock.cancelTask();
    bot.pathfinder.stop();
    bot.pvp.stop();
  }

  clearBotLogs() {
    const bot = this.bot;
    if (!bot) return;
    bot.output = '';
    bot.interrupt_code = false;
  }

  shutUp() {
    this.shut_up = true;
    if (this.self_prompter.isActive()) {
      this.self_prompter.stop(false);
    }
    convoManager.endAllConversations();
  }

  async handleMessage(source: string | null, message: string | null, max_responses: number | null = null) {
    await this.checkTaskDone();
    if (!source || !message) {
      console.warn('Received empty message from', source);
      return false;
    }

    let used_command = false;
    if (max_responses === null) {
      max_responses = appSettings.max_commands === -1 ? Infinity : appSettings.max_commands;
    }
    if (max_responses === -1) {
      max_responses = Infinity;
    }

    const self_prompt = source === 'system' || source === this.name;
    const from_other_bot = convo.isOtherAgent(source);

    if (!self_prompt && !from_other_bot) { // from user, check for forced commands
      const user_command_name = containsCommand(message);
      if (user_command_name) {
        if (!commandExists(user_command_name)) {
          this.routeResponse(source, `Command '${user_command_name}' does not exist.`);
          return false;
        }
        this.routeResponse(source, `*${source} used ${user_command_name.substring(1)}*`);
        if (user_command_name === '!newAction') {
          // all user-initiated commands are ignored by the bot except for this one
          // add the preceding message to the history to give context for newAction
          this.history.add(source, message);
        }
        let execute_res = await executeCommand(this, message);
        if (execute_res)
          this.routeResponse(source, execute_res);
        return true;
      }
    }

    if (from_other_bot)
      this.last_sender = source;

    // Now translate the message
    message = await handleEnglishTranslation(message);
    console.log('received message from', source, ':', message);

    const checkInterrupt = () => this.self_prompter.shouldInterrupt(self_prompt) || this.shut_up || convo.responseScheduledFor(source);

    const bot = this.bot;
    if (!bot) return false;
    let behavior_log = bot.modes.flushBehaviorLog().trim();
    if (behavior_log.length > 0) {
      const MAX_LOG = 500;
      if (behavior_log.length > MAX_LOG) {
        behavior_log = '...' + behavior_log.substring(behavior_log.length - MAX_LOG);
      }
      behavior_log = 'Recent behaviors log: \n' + behavior_log;
    await this.history.add('system', behavior_log);
    }

    // Handle other user messages
    const safeSource = source ?? 'system';
    const safeMessage = message ?? '';
    await this.history.add(safeSource, safeMessage);
    this.history.save();

    if (!self_prompt && this.self_prompter.isActive()) // message is from user during self-prompting
      max_responses = 1; // force only respond to this message, then let self-prompting take over

    for (let i = 0; i < (max_responses ? max_responses : 1); i++) {
      if (checkInterrupt()) break;
      let history = this.history.getHistory();
      let res = await this.prompter.promptConvo(history);
      if (res == null) {
        break;
      }
      res = String(res);
      const response = res;

      console.log(`${this.name} full response to ${safeSource}: ""${response}""`);

      if (response.trim().length === 0) {
        console.warn('no response');
        break; // empty response ends loop
      }

      let command_name = containsCommand(response);
      const commandText = command_name ?? '';

      if (command_name) { // contains query or command
        const commandResponse = truncCommandMessage(response) ?? response;
        this.history.add(this.name, commandResponse);

        if (!commandExists(command_name)) {
          this.history.add('system', `Command ${command_name} does not exist.`);
          console.warn('Agent hallucinated command:', command_name);
          continue;
        }

        if (checkInterrupt()) break;
        this.self_prompter.handleUserPromptedCmd(self_prompt, isAction(command_name));

        if (appSettings.show_command_syntax === "full") {
          this.routeResponse(safeSource, commandResponse);
        }
        else if (appSettings.show_command_syntax === "shortened") {
          // show only "used !commandname"
          let pre_message = commandResponse.substring(0, commandResponse.indexOf(commandText)).trim();
          let chat_message = `*used ${commandText.substring(1)}*`;
          if (pre_message.length > 0)
            chat_message = `${pre_message}  ${chat_message}`;
          this.routeResponse(safeSource, chat_message);
        }
        else {
          // no command at all
          let pre_message = commandResponse.substring(0, commandResponse.indexOf(commandText)).trim();
          if (pre_message.trim().length > 0)
            this.routeResponse(safeSource, pre_message);
        }

        let execute_res = await executeCommand(this, commandResponse);

        console.log('Agent executed:', command_name, 'and got:', execute_res);
        used_command = true;

        if (execute_res)
          this.history.add('system', execute_res);
        else
          break;
      }
      else { // conversation response
        this.history.add(this.name, response);
        this.routeResponse(safeSource, response);
        break;
      }

      this.history.save();
    }

    return used_command;
  }

  async routeResponse(to_player: string, message: string) {
    if (this.shut_up) return;
    let self_prompt = to_player === 'system' || to_player === this.name;
    if (self_prompt && this.last_sender) {
      // this is for when the agent is prompted by system while still in conversation
      // so it can respond to events like death but be routed back to the last sender
      to_player = this.last_sender;
    }

    const conversationTarget = to_player == null ? null : to_player;
    if (conversationTarget != null && convo.isOtherAgent(conversationTarget) && convo.inConversation(conversationTarget)) {
      // if we're in an ongoing conversation with the other bot, send the response to it
      convo.sendToBot(conversationTarget, message);
    }
    else {
      // otherwise, use open chat
      await this.openChat(message);
      // note that to_player could be another bot, but if we get here the conversation has ended
    }
  }

  async openChat(message: string) {
    let to_translate = message;
    let remaining = '';
    let command_name = containsCommand(message);
    let translate_up_to = command_name ? message.indexOf(command_name) : -1;
    if (translate_up_to != -1) { // don't translate the command
      to_translate = to_translate.substring(0, translate_up_to);
      remaining = message.substring(translate_up_to);
    }
    message = (await handleTranslation(to_translate)).trim() + " " + remaining;
    // newlines are interpreted as separate chats, which triggers spam filters. replace them with spaces
    message = message.replaceAll('\n', ' ');

    if (appSettings.only_chat_with.length > 0) {
      const bot = this.bot;
      if (!bot) return;
      for (let username of appSettings.only_chat_with) {
        bot.whisper(username, message);
      }
    }
    else {
      // if (settings.speak) {
      //     speak(to_translate, this.prompter.profile.speak_model);
      // }
      if (appSettings.chat_ingame) { this.bot?.chat(message); }
      sendOutputToServer(this.name, message);
    }
  }

  startEvents() {
    // Custom events
    const bot = this.bot;
    if (!bot) throw new Error('Bot is not initialized');

    bot.on('time', () => {
      if (bot.time.timeOfDay == 0)
        bot.emit('sunrise');
      else if (bot.time.timeOfDay == 6000)
        bot.emit('noon');
      else if (bot.time.timeOfDay == 12000)
        bot.emit('sunset');
      else if (bot.time.timeOfDay == 18000)
        bot.emit('midnight');
    });

    let prev_health = bot.health;
    bot.lastDamageTime = 0;
    bot.lastDamageTaken = 0;
    bot.on('health', () => {
      if (bot.health < prev_health) {
        bot.lastDamageTime = Date.now();
        bot.lastDamageTaken = prev_health - bot.health;
      }
      prev_health = bot.health;
    });
    // Logging callbacks
    bot.on('error', (err: unknown) => {
      if (hasErrorMessage(err)) console.error('Error event!', err);
      else console.error('Error event!', String(err));
    });
    // Use connection handler for runtime disconnects
    bot.on('end', (reason: string) => {
      if (!this._disconnectHandled) {
        const { msg } = handleDisconnection(this.name, reason);
        this.cleanKill(msg);
      }
    });
    bot.on('death', () => {
      this.actions.cancelResume();
      this.actions.stop();
    });
    bot.on('kicked', (reason: string) => {
      if (!this._disconnectHandled) {
        const { msg } = handleDisconnection(this.name, reason);
        this.cleanKill(msg);
      }
    });
    bot.on('messagestr', async (...args: unknown[]) => {
      const [message, , jsonMsg] = args as [string, unknown, { translate?: string } | undefined];
      if (jsonMsg?.translate && jsonMsg.translate.startsWith('death') && message.startsWith(this.name)) {
        console.log('Agent died: ', message);
        let death_pos = bot.entity.position;
        this.memory_bank.rememberPlace('last_death_position', death_pos.x, death_pos.y, death_pos.z);
        let death_pos_text: string | null = null;
        if (death_pos) {
          death_pos_text = `x: ${death_pos.x.toFixed(2)}, y: ${death_pos.y.toFixed(2)}, z: ${death_pos.x.toFixed(2)}`;
        }
        let dimention = bot.game.dimension;
        await this.handleMessage('system', `You died at position ${death_pos_text || "unknown"} in the ${dimention} dimension with the final message: '${message}'. Your place of death is saved as 'last_death_position' if you want to return. Previous actions were stopped and you have respawned.`);
      }
    });
    bot.on('idle', () => {
      bot.clearControlStates();
      bot.pathfinder.stop(); // clear any lingering pathfinder
      bot.modes.unPauseAll();
      setTimeout(() => {
        if (this.isIdle()) {
          this.actions.resumeAction();
        }
      }, 1000);
    });

    // Init NPC controller
    this.npc.init();

    // This update loop ensures that each update() is called one at a time, even if it takes longer than the interval
    const INTERVAL = 300;
    let last: number = Date.now();
    setTimeout(async () => {
      while (true) {
        let start = Date.now();
        await this.update(start - last);
        let remaining = INTERVAL - (Date.now() - start);
        if (remaining > 0) {
          await new Promise((resolve) => setTimeout(resolve, remaining));
        }
        last = start;
      }
    }, INTERVAL);

    bot.emit('idle');
  }

  async update(delta: number) {
    await this.bot!.modes.update();
    this.self_prompter.update(delta);
    await this.checkTaskDone();
  }

  isIdle() {
    return !this.actions.executing;
  }


  cleanKill(msg: string = 'Killing agent process...', code: number = 1) {
    this.history.add('system', msg);
    this.bot!.chat(code > 1 ? 'Restarting.' : 'Exiting.');
    this.history.save();
    process.exit(code);
  }
  async checkTaskDone() {
    if (!this.task) return;

    if (this.task.data) {
      let res = this.task.isDone();
      if (res) {
        await this.history.add('system', `Task ended with score : ${res.score}`);
        this.history.save();
        // await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 second for save to complete
        console.log('Task finished:', res.message);
        this.killAll();
      }
    }
  }

  killAll() {
    serverProxy.shutdown();
  }
}

import { Vec3 } from 'vec3';
import { Camera } from "./camera";
import { readFileSync } from 'fs';
import { Agent } from '../agent';
import type { Bot } from 'mineflayer';

type VisionBot = Bot & {
  look(yaw: number, pitch: number): Promise<void>;
  lookAt(position: Vec3): Promise<void>;
  blockAtCursor(maxDistance: number): { name: string; position: Vec3 } | null;
  players: Record<string, { entity?: { position: Vec3; height: number; yaw: number; pitch: number } | null }>;
  world: unknown;
};

export class VisionInterpreter {
  agent: Agent;
  allow_vision: boolean;
  camera!: Camera;
  fp: string;

  constructor(agent: Agent, allow_vision: boolean) {
    this.agent = agent;
    this.allow_vision = allow_vision;
    this.fp = './bots/' + agent.name + '/screenshots/';
    if (allow_vision) {
      this.camera = new Camera(agent.bot as unknown as VisionBot, this.fp);
    }
  }

  async lookAtPlayer(player_name: string, direction: string) {
    if (!this.allow_vision || !this.agent.prompter.vision_model.sendVisionRequest) {
      return "Vision is disabled. Use other methods to describe the environment.";
    }
    let result = "";
    const bot = this.agent.bot as VisionBot | null;
    if (!bot) return 'Bot is not initialized';
    const player = bot.players[player_name]?.entity;
    if (!player) {
      return `Could not find player ${player_name}`;
    }

    let filename: string;
    if (direction === 'with') {
      await bot.look(player.yaw, player.pitch);
      result = `Looking in the same direction as ${player_name}\n`;
      filename = await this.camera.capture();
    } else {
      await bot.lookAt(new Vec3(player.position.x, player.position.y + player.height, player.position.z));
      result = `Looking at player ${player_name}\n`;
      filename = await this.camera.capture();

    }

    return result + `Image analysis: "${await this.analyzeImage(filename)}"`;
  }

  async lookAtPosition(x: number, y: number, z: number) {
    if (!this.allow_vision || !this.agent.prompter.vision_model.sendVisionRequest) {
      return "Vision is disabled. Use other methods to describe the environment.";
    }
    let result = "";
    const bot = this.agent.bot as VisionBot | null;
    if (!bot) return 'Bot is not initialized';
    await bot.lookAt(new Vec3(x, y + 2, z));
    result = `Looking at coordinate ${x}, ${y}, ${z}\n`;

    let filename = await this.camera.capture();

    return result + `Image analysis: "${await this.analyzeImage(filename)}"`;
  }

  getCenterBlockInfo() {
    const bot = this.agent.bot as VisionBot | null;
    if (!bot) return "Bot is not initialized";
    const maxDistance = 128; // Maximum distance to check for blocks
    const targetBlock = bot.blockAtCursor(maxDistance);

    if (targetBlock) {
      return `Block at center view: ${targetBlock.name} at (${targetBlock.position.x}, ${targetBlock.position.y}, ${targetBlock.position.z})`;
    } else {
      return "No block in center view";
    }
  }

  async analyzeImage(filename: string) {
    try {
      const imageBuffer = readFileSync(`${this.fp}/${filename}.jpg`);
      const messages = this.agent.history.getHistory();

      const blockInfo = this.getCenterBlockInfo();
      const result = await this.agent.prompter.promptVision(messages, imageBuffer);
      return result + `\n${blockInfo}`;

    } catch (error: unknown) {
      console.warn('Error reading image:', error);
      return `Error reading image: ${error instanceof Error ? error.message : String(error)}`;
    }
  }
} 

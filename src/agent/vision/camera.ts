import { Viewer } from 'prismarine-viewer/viewer/lib/viewer';
import { WorldView } from 'prismarine-viewer/viewer/lib/worldView';
import { getBufferFromStream } from 'prismarine-viewer/viewer/lib/simpleUtils';

import * as THREE from 'three';
import { createCanvas } from 'node-canvas-webgl/lib/index';
import { writeFile, stat, mkdir } from 'fs/promises';
import { Stats } from 'fs';
import { Vec3 } from 'vec3';
import { EventEmitter } from 'events';
import type { Bot } from 'mineflayer';

// import { Worker } from 'worker_threads';
// globalThis.Worker = Worker;
type CameraBot = Bot & { version?: string; world: unknown; entity: { position: { x: number; y: number; z: number }; height: number; yaw: number; pitch: number } };
type ScreenshotCanvas = ReturnType<typeof createCanvas>;

export class Camera extends EventEmitter {
  bot: CameraBot;
  fp: string;
  viewDistance = 12;
  width = 800;
  height = 512;
  canvas: ScreenshotCanvas = createCanvas(this.width, this.height);
  renderer = new THREE.WebGLRenderer({ canvas: this.canvas });
  viewer = new Viewer(this.renderer as unknown as WebGLRenderingContext);
  worldView!: ReturnType<typeof WorldView>;

  constructor(bot: CameraBot, fp: string) {
    super();
    this.bot = bot;
    this.fp = fp;
    this._init().then(() => {
      this.emit('ready');
    });
  }

  async _init(): Promise<void> {
    const botPos = this.bot.entity.position;
    const center = new Vec3(botPos.x, botPos.y + this.bot.entity.height, botPos.z);
    this.viewer.setVersion(this.bot.version);
    // Load world
    const worldView = new WorldView(this.bot.world, this.viewDistance, center);
    this.viewer.listen(worldView);
    worldView.listenToBot(this.bot);
    await worldView.init(center);
    this.worldView = worldView;
  }

  async capture(): Promise<string> {
    const center = new Vec3(this.bot.entity.position.x, this.bot.entity.position.y + this.bot.entity.height, this.bot.entity.position.z);
    this.viewer.camera.position.set(center.x, center.y, center.z);
    await this.worldView.updatePosition(center);
    this.viewer.setFirstPersonCamera(this.bot.entity.position, this.bot.entity.yaw, this.bot.entity.pitch);
    this.viewer.update();
    this.renderer.render(this.viewer.scene, this.viewer.camera);

    const imageStream = this.canvas.createJPEGStream({
      bufsize: 4096,
      quality: 100,
      progressive: false
    });

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `screenshot_${timestamp}`;

    const buf = await getBufferFromStream(imageStream);
    await this._ensureScreenshotDirectory();
    await writeFile(`${this.fp}/${filename}.jpg`, buf);
    console.log('saved', filename);
    return filename;
  }

  async _ensureScreenshotDirectory(): Promise<void> {
    let stats: Stats | undefined;
    try {
      stats = await stat(this.fp);
    } catch {
      stats = undefined;
    }
    if (!stats?.isDirectory()) {
      await mkdir(this.fp, { recursive: true });
    }
  }
}

declare module './settings' {
  const settings: {
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
  export default settings;
}

declare module '../settings' {
  const settings: {
    max_messages: number;
  };
  export default settings;
}

declare module '../../settings' {
  const settings: {
    max_messages: number;
  };
  export default settings;
}

declare module '../../../settings' {
  const settings: {
    block_place_delay: number | null;
  };
  export default settings;
}

declare module '../utils/mcdata' {
  export function getBlockId(name: string): number | null;
  export function getAllBlockIds(names: string[]): number[];
  export function getAllItems(): Array<{ id: number; name: string }>;
  export function getEntityId(name: string): number | null;
  export function getAllBiomes(): Array<{ name: string }>;
}

declare module '../../utils/mcdata' {
  export function getBlockId(name: string): number | null;
  export function getAllBlockIds(names: string[]): number[];
  export function getAllItems(): Array<{ id: number; name: string }>;
  export function getEntityId(name: string): number | null;
  export function getAllBiomes(): Array<{ name: string }>;
}

declare module './mindserver_proxy' {
  export const serverProxy: {
    login(): void;
    shutdown(): void;
    getNumOtherAgents(): number;
    setAgent(agent: unknown): void;
    connect(name: string, port: number): Promise<void>;
  };
  export function sendOutputToServer(name: string, message: string): void;
}

declare module '../agent/mindserver_proxy' {
  export const serverProxy: {
    login(): void;
    shutdown(): void;
    getNumOtherAgents(): number;
    setAgent(agent: unknown): void;
    connect(name: string, port: number): Promise<void>;
  };
  export function sendOutputToServer(name: string, message: string): void;
}

declare module '../mindcraft/mindserver' {
  export function logoutAgent(name: string): void;
}

declare module 'mineflayer' {
  interface Bot {
    output: string;
    interrupt_code: boolean;
    entity: { position: import('vec3').Vec3; yaw: number; pitch: number; height: number };
    players: { [username: string]: { entity?: import('prismarine-entity').Entity | null } };
    entities: { [id: string]: import('prismarine-entity').Entity };
    modes: {
      isOn(name: string): boolean;
      pause(name: string): void;
      unpause(name: string): void;
      flushBehaviorLog(): string;
    };
    restrict_to_inventory: boolean;
    lastDamageTime: number;
    lastDamageTaken: number;
    armorManager: { equipAll(): void };
    collectBlock: { cancelTask(): void; collect(block: unknown): Promise<void> };
    pvp: { stop(): void; attack(entity: unknown): void };
    tool: { equipForBlock(block: unknown): Promise<void> };
    pathfinder: {
      stop(): void;
      setMovements(movements: unknown): void;
      goto(goal: unknown, sync?: boolean): Promise<void>;
      getPathTo(...args: unknown[]): { status: string };
    };
    registry: { entitiesByName: { villager: { id: number } } };
    game: { gameMode: string };
    targetDigBlock: { canHarvest(itemId: number | null): boolean; name: string; position: import('vec3').Vec3 } | null;
    heldItem: { type: number } | null;
    openFurnace(block: unknown): Promise<{
      inputItem(): unknown;
      outputItem(): unknown;
      fuelItem(): unknown;
      takeInput(): Promise<unknown>;
      takeOutput(): Promise<unknown>;
      takeFuel(): Promise<unknown>;
      putFuel(itemType: number, metadata: number | null, count: number): Promise<void>;
      putInput(itemType: number, metadata: number | null, count: number): Promise<void>;
    }>; 
    lookAt(target: unknown): Promise<void>;
    openChest(block: unknown): Promise<unknown>;
    openBlock(block: unknown): Promise<unknown>;
    closeWindow(window?: unknown): Promise<void>;
    attack(entity: unknown): Promise<void>;
    equip(item: { name: string; count: number; type?: number }, dest: string): Promise<void>;
    chat(message: string): void;
    whisper(username: string, message: string): void;
    creative: { setInventorySlot(slot: number, item: unknown): Promise<void> };
    inventory: { items(): Array<{ name: string; count: number; type: number }>; slots: Array<{ name: string; count: number; type: number } | null> };
  }
}

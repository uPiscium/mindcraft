import pf from 'mineflayer-pathfinder';
import * as mc from '../../utils/mcdata';
import type { Bot } from 'mineflayer';
import type { Block } from 'prismarine-block';
import type { Entity } from 'prismarine-entity';
import { Vec3 } from 'vec3';

export type WorldBot = Bot & {
    entity: Entity;
    world: { getBiome(position: Vec3): number };
    username: string;
    interrupt_code?: boolean;
    modes?: { isOn(name: string): boolean };
    pathfinder: pf.Pathfinder;
    inventory: { items(): Array<{ name: string; count: number }> };
    entities: Record<string, Entity>;
    blockAt(position: Vec3): Block | null;
    findBlocks(options: { matching: number | number[] | ((block: Block | null) => boolean); maxDistance: number; count: number }): Vec3[];
    nearestEntity(predicate: (entity: Entity) => boolean): Entity | null;
    recipesFor(itemId: number, meta: number | null, count: number, table: Block | boolean | null): unknown[];
};


export function getNearestFreeSpace(bot: WorldBot, size = 1, distance = 8): Vec3 | undefined {
    /**
     * Get the nearest empty space with solid blocks beneath it of the given size.
     * @param {bot} bot - The bot to get the nearest free space for.
     * @param {number} size - The (size x size) of the space to find, default 1.
     * @param {number} distance - The maximum distance to search, default 8.
     * @returns {Vec3} - The south west corner position of the nearest free space.
     * @example
     * let position = world.getNearestFreeSpace(bot, 1, 8);
     **/
    let empty_pos = bot.findBlocks({
        matching: (block: Block | null) => {
            return !!block && block.name === 'air';
        },
        maxDistance: distance,
        count: 1000
    });
    for (let i = 0; i < empty_pos.length; i++) {
        const pos = empty_pos[i];
        if (!pos) continue;
        let empty = true;
        for (let x = 0; x < size; x++) {
            for (let z = 0; z < size; z++) {
                let top = bot.blockAt(pos.offset(x, 0, z));
                let bottom = bot.blockAt(pos.offset(x, -1, z));
                if (!top || top.name !== 'air' || !bottom || (bottom.drops?.length ?? 0) === 0 || !bottom.diggable) {
                    empty = false;
                    break;
                }
            }
            if (!empty) break;
        }
        if (empty) return pos;
    }
}


export function getBlockAtPosition(bot: WorldBot, x = 0, y = 0, z = 0): Block | null {
     /**
     * Get a block from the bot's relative position 
     * @param {bot} bot - The bot to get the block for.
     * @param {number} x - The relative x offset to serach, default 0.
     * @param {number} y - The relative y offset to serach, default 0.
     * @param {number} y - The relative z offset to serach, default 0. 
     * @returns {Block} - The nearest block.
     * @example
     * let blockBelow = world.getBlockAtPosition(bot, 0, -1, 0);
     * let blockAbove = world.getBlockAtPosition(bot, 0, 2, 0); since minecraft position is at the feet
     **/
    return bot.blockAt(bot.entity.position.offset(x, y, z));
}


export function getSurroundingBlocks(bot: WorldBot): string[] {
    /**
     * Get the surrounding blocks from the bot's environment.
     * @param {bot} bot - The bot to get the block for.
     * @returns {string[]} - A list of block results as strings.
     * @example
     **/
    // Create a list of block position results that can be unpacked.
    let res: string[] = [];
    res.push(`Block Below: ${getBlockAtPosition(bot, 0, -1, 0)?.name ?? 'air'}`);
    res.push(`Block at Legs: ${getBlockAtPosition(bot, 0, 0, 0)?.name ?? 'air'}`);
    res.push(`Block at Head: ${getBlockAtPosition(bot, 0, 1, 0)?.name ?? 'air'}`);

    return res;
}


export function getFirstBlockAboveHead(bot: WorldBot, ignore_types: string | string[] | null = null, distance = 32): string {
     /**
     * Searches a column from the bot's position for the first solid block above its head
     * @param {bot} bot - The bot to get the block for.
     * @param {string[]} ignore_types - The names of the blocks to ignore.
     * @param {number} distance - The maximum distance to search, default 32.
     * @returns {string} - The fist block above head.
     * @example
     * let firstBlockAboveHead = world.getFirstBlockAboveHead(bot, null, 32);
     **/
    // if ignore_types is not a list, make it a list.
    let ignore_blocks: string[] = [];
    if (ignore_types === null) ignore_blocks = ['air', 'cave_air'];
    else {
        const ignoreList = Array.isArray(ignore_types) ? ignore_types : [ignore_types];
        for (let ignore_type of ignoreList) {
            if (mc.getBlockId(ignore_type)) ignore_blocks.push(ignore_type);
        }
    }
    // The block above, stops when it finds a solid block .
    let block_above: Block | null = null;
    let height = 0;
    for (let i = 0; i < distance; i++) {
        const block = bot.blockAt(bot.entity.position.offset(0, i+2, 0));
        // Ignore and continue
        if (!block || ignore_blocks.includes(block.name)) continue;
        // Defaults to any block
        block_above = block;
        height = i;
        break;
    }

    if (!block_above || ignore_blocks.includes(block_above.name)) return 'none';
    
    return `${block_above.name} (${height} blocks up)`;
}


export function getNearestBlocks(bot: WorldBot, block_types: string | string[] | null = null, distance = 8, count = 10000): Array<Block | null> {
    /**
     * Get a list of the nearest blocks of the given types.
     * @param {bot} bot - The bot to get the nearest block for.
     * @param {string[]} block_types - The names of the blocks to search for.
     * @param {number} distance - The maximum distance to search, default 16.
     * @param {number} count - The maximum number of blocks to find, default 10000.
     * @returns {Block[]} - The nearest blocks of the given type.
     * @example
     * let woodBlocks = world.getNearestBlocks(bot, ['oak_log', 'birch_log'], 16, 1);
     **/
    // if blocktypes is not a list, make it a list
    let block_ids: number[] = [];
    if (block_types === null) {
        block_ids = mc.getAllBlockIds(['air']);
    }
    else {
        if (!Array.isArray(block_types))
            block_types = [block_types];
        for (let block_type of block_types) {
            const id = mc.getBlockId(block_type);
            if (typeof id === 'number') block_ids.push(id);
        }
    }
    return getNearestBlocksWhere(bot, block_ids, distance, count);  
}

export function getNearestBlocksWhere(bot: WorldBot, predicate: number | number[] | ((block: Block | null) => boolean), distance = 8, count = 10000): Array<Block | null> {
    /**
     * Get a list of the nearest blocks that satisfy the given predicate.
     * @param {bot} bot - The bot to get the nearest blocks for.
     * @param {function} predicate - The predicate to filter the blocks.
     * @param {number} distance - The maximum distance to search, default 16.
     * @param {number} count - The maximum number of blocks to find, default 10000.
     * @returns {Block[]} - The nearest blocks that satisfy the given predicate.
     * @example
     * let waterBlocks = world.getNearestBlocksWhere(bot, block => block.name === 'water', 16, 10);
     **/
    let positions = bot.findBlocks({matching: predicate, maxDistance: distance, count: count});
    let blocks = positions.map(position => bot.blockAt(position));
    return blocks;
}


export function getNearestBlock(bot: WorldBot, block_type: string, distance = 16): Block | null {
     /**
     * Get the nearest block of the given type.
     * @param {bot} bot - The bot to get the nearest block for.
     * @param {string} block_type - The name of the block to search for.
     * @param {number} distance - The maximum distance to search, default 16.
     * @returns {Block} - The nearest block of the given type.
     * @example
     * let coalBlock = world.getNearestBlock(bot, 'coal_ore', 16);
     **/
    let blocks = getNearestBlocks(bot, block_type, distance, 1);
    if (blocks.length > 0) {
        return blocks[0] ?? null;
    }
    return null;
}


export function getNearbyEntities(bot: WorldBot, maxDistance = 16): Entity[] {
    let entities: Array<{ entity: Entity; distance: number }> = [];
    for (const entity of Object.values(bot.entities)) {
        const distance = entity.position.distanceTo(bot.entity.position);
        if (distance > maxDistance) continue;
        entities.push({ entity: entity, distance: distance });
    }
    entities.sort((a, b) => a.distance - b.distance);
    let res: Entity[] = [];
    for (let i = 0; i < entities.length; i++) {
        const entity = entities[i]?.entity;
        if (entity) res.push(entity);
    }
    return res;
}

export function getNearestEntityWhere(bot: WorldBot, predicate: (entity: Entity) => boolean, maxDistance = 16): Entity | null {
    return bot.nearestEntity(entity => predicate(entity) && bot.entity.position.distanceTo(entity.position) < maxDistance);
}


export function getNearbyPlayers(bot: WorldBot, maxDistance = 16): Entity[] {
    if (maxDistance == null) maxDistance = 16;
    let players: Array<{ entity: Entity; distance: number }> = [];
    for (const entity of Object.values(bot.entities)) {
        const distance = entity.position.distanceTo(bot.entity.position);
        if (distance > maxDistance) continue;
        if (entity.type == 'player' && entity.username != bot.username) {
            players.push({ entity: entity, distance: distance });
        } 
    }
    players.sort((a, b) => a.distance - b.distance);
    let res: Entity[] = [];
    for (let i = 0; i < players.length; i++) {
        const entity = players[i]?.entity;
        if (entity) res.push(entity);
    }
    return res;
}

// Helper function to get villager profession from metadata
export function getVillagerProfession(entity: { metadata?: Record<number, unknown> }): string {
    // Villager profession mapping based on metadata
    const professions: Record<number, string> = {
        0: 'Unemployed',
        1: 'Armorer',
        2: 'Butcher', 
        3: 'Cartographer',
        4: 'Cleric',
        5: 'Farmer',
        6: 'Fisherman',
        7: 'Fletcher',
        8: 'Leatherworker',
        9: 'Librarian',
        10: 'Mason',
        11: 'Nitwit',
        12: 'Shepherd',
        13: 'Toolsmith',
        14: 'Weaponsmith'
    };
    
    if (entity.metadata && entity.metadata[18]) {
        // Check if metadata[18] is an object with villagerProfession property
        if (typeof entity.metadata[18] === 'object' && entity.metadata[18] !== null && 'villagerProfession' in entity.metadata[18]) {
            const meta = entity.metadata[18] as { villagerProfession?: number; level?: number };
            const professionId = meta.villagerProfession;
            const level = meta.level || 1;
            const professionName = professionId != null ? professions[professionId] || 'Unknown' : 'Unknown';
            return `${professionName} L${level}`;
        }
        // Fallback for direct profession ID
        else if (typeof entity.metadata[18] === 'number') {
            const professionId = entity.metadata[18] as number;
            return professions[professionId] || 'Unknown';
        }
    }
    
    // If we can't determine profession but it's an adult villager
    if (entity.metadata && entity.metadata[16] !== 1) { // Not a baby
        return 'Adult';
    }
    
    return 'Unknown';
}


export function getInventoryStacks(bot: WorldBot): Array<{ name: string; count: number }> {
    let inventory: Array<{ name: string; count: number }> = [];
    for (const item of bot.inventory.items()) {
        if (item != null) {
            inventory.push(item);
        }
    }
    return inventory;
}


export function getInventoryCounts(bot: WorldBot): Record<string, number> {
    /**
     * Get an object representing the bot's inventory.
     * @param {bot} bot - The bot to get the inventory for.
     * @returns {object} - An object with item names as keys and counts as values.
     * @example
     * let inventory = world.getInventoryCounts(bot);
     * let oakLogCount = inventory['oak_log'];
     * let hasWoodenPickaxe = inventory['wooden_pickaxe'] > 0;
     **/
    let inventory: Record<string, number> = {};
    for (const item of bot.inventory.items()) {
        if (!item) continue;
        inventory[item.name] = (inventory[item.name] ?? 0) + item.count;
    }
    return inventory;
}


export function getCraftableItems(bot: WorldBot): string[] {
    /**
     * Get a list of all items that can be crafted with the bot's current inventory.
     * @param {bot} bot - The bot to get the craftable items for.
     * @returns {string[]} - A list of all items that can be crafted.
     * @example
     * let craftableItems = world.getCraftableItems(bot);
     **/
    let table: Block | boolean | null = getNearestBlock(bot, 'crafting_table');
    if (!table) {
        for (const item of bot.inventory.items()) {
            if (item != null && item.name === 'crafting_table') {
                table = true;
                break;
            }
        }
    }
    let res: string[] = [];
    for (const item of mc.getAllItems()) {
        let recipes = bot.recipesFor(item.id, null, 1, table);
        if (recipes.length > 0)
            res.push(item.name);
    }
    return res;
}


export function getPosition(bot: WorldBot): Vec3 {
    /**
     * Get your position in the world (Note that y is vertical).
     * @param {bot} bot - The bot to get the position for.
     * @returns {Vec3} - An object with x, y, and x attributes representing the position of the bot.
     * @example
     * let position = world.getPosition(bot);
     * let x = position.x;
     **/
    return bot.entity.position;
}


export function getNearbyEntityTypes(bot: WorldBot): string[] {
    /**
     * Get a list of all nearby mob types.
     * @param {bot} bot - The bot to get nearby mobs for.
     * @returns {string[]} - A list of all nearby mobs.
     * @example
     * let mobs = world.getNearbyEntityTypes(bot);
     **/
    let mobs = getNearbyEntities(bot, 16);
    let found: string[] = [];
    for (let i = 0; i < mobs.length; i++) {
        const name = mobs[i]?.name;
        if (name && !found.includes(name)) {
            found.push(name);
        }
    }
    return found;
}

export function isEntityType(name: string): boolean {
    /**
     * Check if a given name is a valid entity type.
     * @param {string} name - The name of the entity type to check.
     * @returns {boolean} - True if the name is a valid entity type, false otherwise.
     */
    return mc.getEntityId(name) !== null;
}

export function getNearbyPlayerNames(bot: WorldBot): string[] {
    /**
     * Get a list of all nearby player names.
     * @param {bot} bot - The bot to get nearby players for.
     * @returns {string[]} - A list of all nearby players.
     * @example
     * let players = world.getNearbyPlayerNames(bot);
     **/
    let players = getNearbyPlayers(bot, 64);
    let found: string[] = [];
    for (let i = 0; i < players.length; i++) {
        const username = players[i]?.username;
        if (username && !found.includes(username) && username !== bot.username) {
            found.push(username);
        }
    }
    return found;
}


export function getNearbyBlockTypes(bot: WorldBot, distance = 16): string[] {
    /**
     * Get a list of all nearby block names.
     * @param {bot} bot - The bot to get nearby blocks for.
     * @param {number} distance - The maximum distance to search, default 16.
     * @returns {string[]} - A list of all nearby blocks.
     * @example
     * let blocks = world.getNearbyBlockTypes(bot);
     **/
    let blocks = getNearestBlocks(bot, null, distance);
    let found: string[] = [];
    for (let i = 0; i < blocks.length; i++) {
        const name = blocks[i]?.name;
        if (name && !found.includes(name)) {
            found.push(name);
        }
    }
    return found;
}

export async function isClearPath(bot: WorldBot, target: { position: Vec3 }): Promise<boolean> {
    /**
     * Check if there is a path to the target that requires no digging or placing blocks.
     * @param {bot} bot - The bot to get the path for.
     * @param {Entity} target - The target to path to.
     * @returns {boolean} - True if there is a clear path, false otherwise.
     */
    let movements = new pf.Movements(bot);
    movements.canDig = false;
    movements.canOpenDoors = false;
    let goal = new pf.goals.GoalNear(target.position.x, target.position.y, target.position.z, 1);
    let path = await bot.pathfinder.getPathTo(movements, goal, 100);
    return path.status === 'success';
}

export function shouldPlaceTorch(bot: WorldBot): boolean {
    if (!bot.modes?.isOn('torch_placing') || bot.interrupt_code) return false;
    const pos = getPosition(bot);
    // TODO: check light level instead of nearby torches, block.light is broken
    let nearest_torch = getNearestBlock(bot, 'torch', 6);
    if (!nearest_torch)
        nearest_torch = getNearestBlock(bot, 'wall_torch', 6);
    if (!nearest_torch) {
        const block = bot.blockAt(pos);
        let has_torch = bot.inventory.items().some(item => item.name === 'torch');
        return Boolean(has_torch && block?.name === 'air');
    }
    return false;
}

export function getBiomeName(bot: WorldBot): string {
    /**
     * Get the name of the biome the bot is in.
     * @param {bot} bot - The bot to get the biome for.
     * @returns {string} - The name of the biome.
     * @example
     * let biome = world.getBiomeName(bot);
     **/
    const biomeId = bot.world.getBiome(bot.entity.position);
    return mc.getAllBiomes()[biomeId]?.name ?? 'unknown';
}

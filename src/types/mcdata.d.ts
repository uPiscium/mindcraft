declare module '../utils/mcdata' {
  export function getBlockId(name: string): number | null;
  export function getAllBlockIds(names: string[]): number[];
  export function getAllItems(): Array<{ id: number; name: string }>;
  export function getEntityId(name: string): number | null;
  export function getAllBiomes(): Array<{ name: string }>;
  export function initBot(name: string): unknown;
}

declare module '../../utils/mcdata' {
  export function getBlockId(name: string): number | null;
  export function getAllBlockIds(names: string[]): number[];
  export function getAllItems(): Array<{ id: number; name: string }>;
  export function getEntityId(name: string): number | null;
  export function getAllBiomes(): Array<{ name: string }>;
  export function initBot(name: string): unknown;
}

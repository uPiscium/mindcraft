export interface SettingsState {
  profile: { skin?: { model: string; path: string } };
  task: string;
  blocked_actions: string[];
  spawn_timeout: number;
  allow_vision: boolean;
  only_chat_with: string[];
  max_commands: number;
  show_command_syntax: 'full' | 'shortened' | 'off';
  chat_ingame: boolean;
  minecraft_version?: string;
  host?: string;
  port?: number;
  auth?: string;
  block_place_delay?: number | null;
  max_messages?: number;
  [key: string]: unknown;
}

const settings = {} as SettingsState;

export default settings;

export function setSettings(newSettings: Partial<SettingsState>): void {
  for (const key of Object.keys(settings)) {
    delete settings[key];
  }
  Object.assign(settings, newSettings);
}

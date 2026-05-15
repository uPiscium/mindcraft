import baseSettings from '../../settings.js';
import { applyEnvOverrides, validateSettings } from './settings-schema.js';

export function loadSettings(env) {
  const settings = structuredClone(baseSettings);
  applyEnvOverrides(settings, env);
  validateSettings(settings);
  return settings;
}

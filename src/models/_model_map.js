import { normalizeModelDescriptor } from '../config/model.js';
import { resolveProvider } from '../config/provider-registry.js';

const apiMap = new Proxy({}, {
    get(_, api) {
        return resolveProvider(api);
    },
});

export function selectAPI(profile) {
    return normalizeModelDescriptor(profile);
}

export function createModel(profile) {
  const normalized = normalizeModelDescriptor(profile);
  const model = new apiMap[normalized.api](normalized.model, normalized.url, normalized.params);
  return model;
}

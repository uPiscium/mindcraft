import util from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

const RESET = '\x1b[0m';
const PROJECT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const SOURCE_RULES = [
    { match: '/src/agent/tasks/', label: 'Task', color: '\x1b[35m' },
    { match: '/src/agent/', label: 'Agent', color: '\x1b[32m' },
    { match: '/src/models/', label: 'Model', color: '\x1b[36m' },
    { match: '/src/mindcraft/', label: 'MindServer', color: '\x1b[34m' },
    { match: '/src/utils/', label: 'Utils', color: '\x1b[90m' },
    { match: '/tasks/', label: 'Tasks', color: '\x1b[35m' },
    { match: '/main.js', label: 'System', color: '\x1b[36m' },
];
const LEVEL_COLORS = {
    log: '',
    warn: '\x1b[33m',
    error: '\x1b[31m',
};

function formatValue(value) {
    if (typeof value === 'string') {
        return value;
    }
    return util.inspect(value, { colors: false, depth: null, breakLength: Infinity });
}

function getCallerFile() {
    const stack = new Error().stack?.split('\n') ?? [];
    for (const line of stack.slice(2)) {
        const match = line.match(/\(?(.+):(\d+):(\d+)\)?$/);
        if (!match) continue;
        const filePath = match[1];
        if (!filePath.includes('logging.js')) {
            try {
                return filePath.startsWith('file://') ? fileURLToPath(filePath) : filePath;
            } catch {
                return filePath;
            }
        }
    }
    return null;
}

function getSourceInfo(filePath) {
    if (!filePath) {
        return { label: 'System', color: '\x1b[36m' };
    }

    const normalized = path.resolve(filePath);
    const relative = normalized.startsWith(PROJECT_ROOT)
        ? normalized.slice(PROJECT_ROOT.length)
        : normalized;

    for (const rule of SOURCE_RULES) {
        if (relative.includes(rule.match)) {
            return { label: rule.label, color: rule.color };
        }
    }

    return { label: 'System', color: '\x1b[36m' };
}

function formatLine(level, args, source) {
    const levelPrefix = level === 'log' ? '' : level === 'warn' ? 'WARN ' : 'ERROR ';
    const body = args.map(formatValue).join(' ');
    const prefixColor = source.color || LEVEL_COLORS[level] || '';
    const suffix = body ? ` ${body}` : '';
    return `${prefixColor}[${source.label}]${levelPrefix ? `[${levelPrefix.trim()}]` : ''}${RESET}${suffix}`;
}

export function installConsoleFormatting() {
    if (globalThis.__mindcraftConsoleFormattingInstalled) {
        return;
    }

    globalThis.__mindcraftConsoleFormattingInstalled = true;

    const originalLog = console.log.bind(console);
    const originalWarn = console.warn.bind(console);
    const originalError = console.error.bind(console);

    console.log = (...args) => {
        const source = getSourceInfo(getCallerFile());
        originalLog(formatLine('log', args, source));
    };
    console.warn = (...args) => {
        const source = getSourceInfo(getCallerFile());
        originalWarn(formatLine('warn', args, source));
    };
    console.error = (...args) => {
        const source = getSourceInfo(getCallerFile());
        originalError(formatLine('error', args, source));
    };
}

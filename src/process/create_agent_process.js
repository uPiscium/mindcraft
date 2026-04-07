import { NodeAgentProcess } from '../../mindcraft_py/node_agent_process.js';
import { MockAgentClient } from './mock_agent_client.js';

export function createAgentProcess(agentName, mindserverPort, settings) {
    if (settings.mock_client) {
        return new MockAgentClient(agentName, mindserverPort, settings);
    }
    return new NodeAgentProcess(agentName, mindserverPort);
}

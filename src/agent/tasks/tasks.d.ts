export class Task {
  blocked_actions: string[];
  agent_names?: string[];
  data?: unknown;
  taskStartTime?: number;
  constructor(agent: unknown, task: string, taskStart?: number | null | undefined);
  initBotTask(): void;
  setAgentGoal(): void;
  isDone(): { score: number; message: string } | null;
}

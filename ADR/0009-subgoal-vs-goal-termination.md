# ADR 0009: Subgoal vs Goal Termination

## Status

Accepted

## Context

The agent was using `!endGoal` for both intermediate milestones and final task completion. That made the runtime ambiguous: a small step finishing and the whole task finishing looked the same in logs, prompts, and task flow.

This ambiguity made it harder to tell when the agent should continue to the next subtask versus when it should stop the overall self-prompt loop.

## Decision

We will separate milestone completion from whole-task completion.

The chosen split is:

- `!endSubGoal` marks a subtask or milestone as complete while keeping the current task active
- `!endGoal` marks the entire task as complete and stops self-prompting
- prompt examples should teach the model to prefer `!endSubGoal` for intermediate progress and `!endGoal` only for final completion

## Consequences

### Positive

- logs become easier to interpret
- task progress and final completion are no longer conflated
- the agent can keep working through a multi-step task without implying the full goal is done
- prompt behavior can explicitly teach milestone completion

### Negative

- one more command is added
- prompt examples must stay aligned with the new distinction

### Neutral

- this does not change the underlying task pool state machine directly
- the split is mostly semantic at the command/prompt layer for now

## Related Files

- `src/agent/commands/actions.js`
- `src/agent/tasks/tasks.js`
- `profiles/defaults/_default.json`

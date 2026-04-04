from __future__ import annotations


STOPPED = 0
ACTIVE = 1
PAUSED = 2


class SelfPrompterState:
    def __init__(self):
        self.state = STOPPED
        self.loop_active = False
        self.interrupt = False
        self.prompt = ""
        self.idle_time = 0
        self.cooldown = 2000

    def start(self, prompt=None):
        if not prompt:
            if not self.prompt:
                return "No prompt specified. Ignoring request."
            prompt = self.prompt
        self.state = ACTIVE
        self.prompt = prompt
        return None

    def stop(self):
        self.interrupt = True
        self.state = STOPPED

    def pause(self):
        self.interrupt = True
        self.state = PAUSED

    def handle_load(self, prompt, state=None):
        if state is None:
            state = STOPPED
        self.state = state
        self.prompt = prompt or ""
        if state != STOPPED and not prompt:
            raise ValueError("No prompt loaded when self-prompting is active")
        return self.start(prompt) if state == ACTIVE else None

    def is_active(self):
        return self.state == ACTIVE

    def is_stopped(self):
        return self.state == STOPPED

    def is_paused(self):
        return self.state == PAUSED

    def should_interrupt(self, is_self_prompt):
        return is_self_prompt and self.state in (ACTIVE, PAUSED) and self.interrupt

    def handle_user_prompted_cmd(self, is_self_prompt, is_action):
        if not is_self_prompt and is_action:
            self.interrupt = True

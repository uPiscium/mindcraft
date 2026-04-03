from __future__ import annotations


class ActionManager:
    def __init__(self):
        self.executing = False
        self.current_action_label = ""
        self.current_action_fn = None
        self.timedout = False
        self.resume_func = None
        self.resume_name = ""

    def cancel_resume(self):
        self.resume_func = None
        self.resume_name = None

    def get_bot_output_summary(self, output, interrupt_code=False):
        if interrupt_code and not self.timedout:
            return ""
        if len(output) > 500:
            return (
                f"Action output is very long ({len(output)} chars) and has been shortened.\n"
                f"First outputs:\n{output[:250]}\n...skipping many lines.\nFinal outputs:\n {output[-250:]}"
            )
        return "Action output:\n" + str(output)

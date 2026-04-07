from __future__ import annotations

import re


def stringify_turns(turns):
    res = ""
    for turn in turns:
        if turn["role"] == "assistant":
            res += f"\nYour output:\n{turn['content']}"
        elif turn["role"] == "system":
            res += f"\nSystem output: {turn['content']}"
        else:
            res += f"\nUser input: {turn['content']}"
    return res.strip()


def to_single_prompt(turns, system=None, stop_seq="***", model_nickname="assistant"):
    prompt = f"{system}{stop_seq}" if system else ""
    role = ""
    for message in turns:
        role = message["role"]
        if role == "assistant":
            role = model_nickname
        prompt += f"{role}: {message['content']}{stop_seq}"
    if role != model_nickname:
        prompt += model_nickname + ": "
    return prompt


def _get_words(text):
    return re.sub(r"[^a-zA-Z ]", "", text).lower().split(" ")


def word_overlap_score(text1, text2):
    words1 = _get_words(text1)
    words2 = _get_words(text2)
    intersection = [word for word in words1 if word in words2]
    return len(intersection) / (len(words1) + len(words2) - len(intersection))


def strict_format(turns):
    prev_role = None
    messages = []
    filler = {"role": "user", "content": "_"}
    for msg in turns:
        if isinstance(msg.get("content"), str):
            msg = dict(msg)
            msg["content"] = msg["content"].strip()
        if msg["role"] == "system":
            msg = dict(msg)
            msg["role"] = "user"
            msg["content"] = "SYSTEM: " + msg["content"]
        if msg["role"] == prev_role and msg["role"] == "assistant":
            messages.append(filler)
            messages.append(msg)
        elif msg["role"] == prev_role:
            messages[-1] = {
                **messages[-1],
                "content": messages[-1]["content"] + "\n" + msg["content"],
            }
        else:
            messages.append(msg)
        prev_role = msg["role"]

    if messages and messages[0]["role"] != "user":
        messages.insert(0, filler)
    if not messages:
        messages.append(filler)
    return messages


stringifyTurns = stringify_turns
toSinglePrompt = to_single_prompt
wordOverlapScore = word_overlap_score
strictFormat = strict_format

from mindcraft_py.utils.text import (
    strict_format,
    stringify_turns,
    to_single_prompt,
    word_overlap_score,
)


def test_stringify_turns_matches_expected_layout():
    turns = [
        {"role": "system", "content": "hello"},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hey"},
    ]

    assert (
        stringify_turns(turns)
        == "System output: hello\nUser input: hi\nYour output:\nhey"
    )


def test_to_single_prompt_adds_model_prompt_when_needed():
    prompt = to_single_prompt(
        [{"role": "user", "content": "hi"}],
        system="SYSTEM",
        stop_seq="***",
        model_nickname="assistant",
    )

    assert prompt == "SYSTEM***user: hi***assistant: "


def test_word_overlap_score_uses_token_overlap():
    assert word_overlap_score("oak log", "oak plank") > 0
    assert word_overlap_score("oak log", "cobblestone") == 0


def test_strict_format_normalizes_system_and_repeated_roles():
    turns = [
        {"role": "system", "content": " setup "},
        {"role": "user", "content": "first"},
        {"role": "user", "content": "second"},
        {"role": "assistant", "content": "one"},
        {"role": "assistant", "content": "two"},
    ]

    assert strict_format(turns) == [
        {"role": "user", "content": "SYSTEM: setup\nfirst\nsecond"},
        {"role": "assistant", "content": "one"},
        {"role": "user", "content": "_"},
        {"role": "assistant", "content": "two"},
    ]

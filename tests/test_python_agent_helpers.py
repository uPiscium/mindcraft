from mindcraft_py.action_manager import ActionManager
from mindcraft_py.conversation import (
    Conversation,
    ConversationManager,
    compile_in_messages,
    tag_message,
)
from mindcraft_py.history import History
from mindcraft_py.mindserver_proxy import (
    MindServerProxy,
    send_bot_chat_to_server,
    send_output_to_server,
)


def test_history_save_load_round_trip(tmp_path):
    hist = History("Andy", base_dir=tmp_path)
    hist.turns = [{"role": "user", "content": "hello"}]
    hist.memory = "memo"
    hist.save(
        self_prompting_state=True, self_prompt="prompt", task_start=1, last_sender="bob"
    )

    reloaded = History("Andy", base_dir=tmp_path)
    data = reloaded.load()

    assert data is not None
    assert data["memory"] == "memo"
    assert reloaded.turns == [{"role": "user", "content": "hello"}]


def test_conversation_helpers():
    convo = Conversation("Bob")
    convo.queue({"message": "hello"})
    convo.queue({"message": " world"})
    assert compile_in_messages(convo)["message"] == "hello world"
    assert tag_message("hi") == "(FROM OTHER BOT)hi"


def test_action_manager_summary():
    am = ActionManager()
    assert am.get_bot_output_summary("ok") == "Action output:\nok"


def test_mindserver_proxy_helpers():
    proxy = MindServerProxy()
    proxy.set_agents([{"name": "Andy"}, {"name": "Bob"}])
    assert proxy.get_num_other_agents() == 1
    assert send_bot_chat_to_server("Andy", {"message": "hi"})["agentName"] == "Andy"
    assert send_output_to_server("Andy", "hello")["message"] == "hello"

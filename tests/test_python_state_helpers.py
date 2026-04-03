from mindcraft_py.connection_handler import (
    handle_disconnection,
    parse_kick_reason,
    validate_name_format,
)
from mindcraft_py.memory_bank import MemoryBank
from mindcraft_py.settings import set_settings, settings


def test_settings_are_mutable_singleton_dict():
    set_settings({"foo": 1})
    assert settings["foo"] == 1


def test_memory_bank_round_trip():
    bank = MemoryBank()
    bank.remember_place("base", 1, 2, 3)
    assert bank.recall_place("base") == [1, 2, 3]
    assert bank.get_keys() == "base"


def test_connection_handler_parses_and_validates():
    assert validate_name_format("Player_1")["success"] is True
    assert validate_name_format("ab")["success"] is False
    assert parse_kick_reason("Server is full")["type"] == "server_full"
    assert handle_disconnection("Andy", "maintenance")["msg"].startswith("[LoginGuard]")

from mindcraft_py.environment import FilterInventoryByContext, TranslateSpatialData


def test_translate_spatial_data_avoids_raw_coordinates_and_marks_interaction():
    result = TranslateSpatialData(
        {"x": 0, "y": 64, "z": 0},
        [{"x": 2, "y": 64, "z": -3}, {"x": 0, "y": 64, "z": 10}],
        threshold_distance=5,
    )

    assert "3.6" in result
    assert "North" in result
    assert "相互作用可能" in result
    assert "相互作用不可" in result
    assert "64" not in result
    assert "0," not in result


def test_filter_inventory_by_context_uses_keyword_lookup_only():
    result = FilterInventoryByContext(
        {"oak_log": 12, "torch": {"quantity": 4}, "stone": 99},
        ["oak_log", "torch", "diamond"],
    )

    assert result == "oak_log: 12; torch: 4"

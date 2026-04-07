from __future__ import annotations

from math import sqrt
from typing import Any


def _extract_vector_components(vector: Any) -> tuple[float, float, float]:
    if isinstance(vector, dict):
        return (
            float(vector.get("x", 0.0)),
            float(vector.get("y", 0.0)),
            float(vector.get("z", 0.0)),
        )
    if hasattr(vector, "x") and hasattr(vector, "y") and hasattr(vector, "z"):
        return (float(vector.x), float(vector.y), float(vector.z))
    x, y, z = vector
    return (float(x), float(y), float(z))


def _direction_from_delta(dx: float, dz: float) -> str:
    directions: list[str] = []
    if dz < 0:
        directions.append("North")
    elif dz > 0:
        directions.append("South")
    if dx > 0:
        directions.append("East")
    elif dx < 0:
        directions.append("West")
    return "-".join(directions) if directions else "Same position"


def TranslateSpatialData(
    self_position: Any,
    target_positions: list[Any],
    threshold_distance: float,
) -> str:
    self_x, self_y, self_z = _extract_vector_components(self_position)
    summaries: list[str] = []

    for index, target in enumerate(target_positions, start=1):
        target_x, target_y, target_z = _extract_vector_components(target)
        dx = target_x - self_x
        dy = target_y - self_y
        dz = target_z - self_z
        distance = sqrt(dx * dx + dy * dy + dz * dz)
        direction = _direction_from_delta(dx, dz)
        status = "相互作用可能"
        if distance > threshold_distance:
            status = "相互作用不可"
        summaries.append(
            f"Target {index}: {distance:.1f} blocks to {direction}, {status}"
        )

    return "; ".join(summaries)


def _extract_inventory_quantity(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, dict):
        for key in ("quantity", "count", "amount", "qty"):
            if key in value:
                return _extract_inventory_quantity(value[key])
        return 0
    if isinstance(value, list):
        return len(value)
    return 0


def FilterInventoryByContext(
    inventory: dict[str, Any], task_keywords: list[str]
) -> str:
    summaries: list[str] = []

    for keyword in task_keywords:
        candidates = [keyword, keyword.lower(), keyword.upper(), keyword.title()]
        matched_value = None
        matched_key = None
        for candidate in candidates:
            if candidate in inventory:
                matched_key = candidate
                matched_value = inventory[candidate]
                break

        if matched_value is None:
            continue

        quantity = _extract_inventory_quantity(matched_value)
        summaries.append(f"{matched_key}: {quantity}")

    return "; ".join(summaries) if summaries else "No context-matched inventory items."


TranslateSpatialData = TranslateSpatialData
FilterInventoryByContext = FilterInventoryByContext

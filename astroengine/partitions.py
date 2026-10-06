"""Half-open uniform angular partitions without floating floor-boundary drift."""

import math
from bisect import bisect_right

from .models import CalculationError


def uniform_partition(value: float, count: int, span: float = 360,
                      origin: float = 0) -> tuple[int, float]:
    """Return index/fraction; callers normalize into [origin, origin + span)."""
    if count <= 0 or not math.isfinite(value) or not origin <= value < origin + span:
        raise CalculationError('Invalid angular partition input')
    boundaries = [origin + index * span / count for index in range(count + 1)]
    index = bisect_right(boundaries, value) - 1
    fraction = (value - boundaries[index]) / (boundaries[index + 1] - boundaries[index])
    return index, fraction

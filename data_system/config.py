# Cấu hình cho data_system
from dataclasses import dataclass

@dataclass
class GraphConfig:

    TRAIN_SPEED_KMH: float = 38.0

    TRAIN_COST_YEN: float = 150.0

    TRAIN_COST_PER_KM = 35.0

    WALK_TIME_SAME_ZONE_MIN: float = 5.0

    WALK_TIME_DIFF_ZONE_MIN: float = 10.0

    MAX_TRANSFER_DISTANCE_KM: float = 0.35

    TRANSFER_PENALTY_MIN: float = 8.0

config = GraphConfig()

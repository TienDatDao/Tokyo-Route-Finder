# Cấu hình cho data_system
from dataclasses import dataclass

@dataclass
class GraphConfig:
    # Tốc độ tàu trung bình (km/h)
    TRAIN_SPEED_KMH: float = 40.0
    # Phí mỗi đoạn tàu (yen)
    TRAIN_COST_YEN: float = 150.0
    # Thời gian đi bộ trong cùng fare zone (phút)
    WALK_TIME_SAME_ZONE_MIN: float = 2.0
    # Thời gian đi bộ khác fare zone (phút)
    WALK_TIME_DIFF_ZONE_MIN: float = 7.0

# Instance global
config = GraphConfig()

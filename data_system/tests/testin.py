from pathlib import Path

from data_system.core.station_group_resolver import (
    StationGroupResolver
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

path = BASE_DIR / "data_system" / "raw_data" / "station_groups.json"

resolver = StationGroupResolver(path)

if __name__ == '__main__':

    print(
        resolver.resolve("Osaki")
    )
import json
from pathlib import Path


class StationGroupResolver:

    def __init__(self, station_groups_path):

        self.station_groups_path = station_groups_path

        self.group_map = {}

        self._load()

    def _load(self):

        with open(
            self.station_groups_path,
            'r',
            encoding='utf-8'
        ) as f:

            data = json.load(f)

        for big_group in data:

            all_nodes = []

            for subgroup in big_group:

                for node_id in subgroup:

                    all_nodes.append(node_id)

            if not all_nodes:
                continue

            # lấy tên ga từ node đầu
            # JR-East.Yamanote.Osaki
            # -> Osaki

            station_name = (
                all_nodes[0]
                .split(".")[-1]
            )

            self.group_map[station_name] = all_nodes

    def resolve(self, station_name):

        return self.group_map.get(
            station_name,
            []
        )
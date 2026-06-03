import heapq
import math
import itertools


# =========================================================
# HELPERS
# =========================================================

def normalize_line(line):

    if not line:
        return None

    line = line.lower()

    if (
        line == 'walk'
        or line == '__walk__'
    ):
        return None

    line = (
        line
        .replace('jr ', '')
        .replace(' line', '')
        .replace('line ', '')
        .strip()
    )

    return line


def calculate_haversine_km(
        lat1,
        lon1,
        lat2,
        lon2
):

    R = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


# =========================================================
# HEURISTIC
# =========================================================

def heuristic(
        current,
        goals,
        graph,
        criteria
):

    if current not in graph or not goals:
        return 0

    if not isinstance(
            goals,
            (list, set, tuple)
    ):
        goals = [goals]

    lat1 = graph[current]["metadata"]["lat"]
    lon1 = graph[current]["metadata"]["lon"]

    best_heuristic = float('inf')

    for goal in goals:

        if goal not in graph:
            continue

        lat2 = graph[goal]["metadata"]["lat"]
        lon2 = graph[goal]["metadata"]["lon"]

        distance_km = calculate_haversine_km(
            lat1,
            lon1,
            lat2,
            lon2
        )

        # ======================================
        # SHORTEST TIME
        # ======================================

        if criteria == "shortest_time":

            # optimistic train speed
            estimated_minutes = (
                distance_km / 35
            ) * 60

            best_heuristic = min(
                best_heuristic,
                estimated_minutes
            )

        # ======================================
        # LOWEST COST
        # ======================================

        elif criteria == "lowest_cost":

            # use Dijkstra
            best_heuristic = 0

        # ======================================
        # LEAST TRANSFERS
        # ======================================

        elif criteria == "least_transfers":

            # use Dijkstra
            best_heuristic = 0

        else:

            best_heuristic = 0

    return (
        best_heuristic
        if best_heuristic != float('inf')
        else 0
    )


# =========================================================
# MAIN
# =========================================================

def find_optimal_route(
        graph,
        start,
        end,
        criteria
):

    start_nodes = (
        [start]
        if isinstance(start, str)
        else list(start)
    )

    end_nodes = (
        [end]
        if isinstance(end, str)
        else list(end)
    )

    start_nodes = [
        node
        for node in start_nodes
        if node in graph
    ]

    end_nodes = [
        node
        for node in end_nodes
        if node in graph
    ]

    if not start_nodes or not end_nodes:
        return {"status": "NO_ROUTE_FOUND"}

    # =====================================================
    # SAME STATION
    # =====================================================

    end_set = set(end_nodes)

    for start_node in start_nodes:

        if start_node in end_set:

            return {
                "status": "SUCCESS",
                "route": {
                    "path": [start_node],
                    "total_time": 0,
                    "total_cost": 0,
                    "transfers": 0,
                    "details": [
                        {
                            "station_id": start_node,
                            "station_name":
                                graph[start_node]["metadata"].get(
                                    "name",
                                    start_node
                                ),
                            "line": None,
                            "action": "Arrive"
                        }
                    ]
                }
            }

    # =====================================================
    # A*
    # =====================================================

    pq = []

    counter = itertools.count()

    best_g = {}

    came_from = {}

    for start_node in start_nodes:

        h = heuristic(
            start_node,
            end_nodes,
            graph,
            criteria
        )

        heapq.heappush(
            pq,
            (
                h,
                next(counter),
                0,
                start_node,
                None,
                0,
                0,
                0
            )
        )

        best_g[(start_node, None)] = 0

    # =====================================================
    # SEARCH
    # =====================================================

    while pq:

        (
            f,
            _,
            g,
            current,
            current_line,
            curr_time,
            curr_cost,
            curr_transfers
        ) = heapq.heappop(pq)

        # ==============================================
        # GOAL
        # ==============================================

        if current in end_set:

            return reconstruct_path(
                came_from,
                start_nodes,
                current,
                current_line,
                curr_time,
                curr_cost,
                curr_transfers,
                graph
            )

        # ==============================================
        # SKIP WORSE STATE
        # ==============================================

        if (
            best_g.get(
                (current, current_line),
                float('inf')
            ) < g
        ):
            continue

        current_line_norm = normalize_line(
            current_line
        )

        # ==============================================
        # EXPLORE EDGES
        # ==============================================

        for edge in graph[current]["connections"]:

            neighbor = edge["to"]

            neighbor_line_raw = edge.get("line")

            neighbor_line_norm = normalize_line(
                neighbor_line_raw
            )

            # ==========================================
            # TRANSFER DETECTION
            # ==========================================

            is_transfer = (
                current_line_norm is not None
                and neighbor_line_norm is not None
                and current_line_norm != neighbor_line_norm
            )

            # ==========================================
            # ACCUMULATED VALUES
            # ==========================================

            edge_time = edge.get("time", 0)

            edge_cost = edge.get("cost", 0)

            next_time = (
                curr_time
                + edge_time
            )

            next_cost = (
                curr_cost
                + edge_cost
            )

            next_transfers = (
                curr_transfers
                + (1 if is_transfer else 0)
            )

            # ==========================================
            # WEIGHT FUNCTION
            # ==========================================

            if criteria == "shortest_time":

                weight = edge_time

                # very small transfer penalty
                if is_transfer:
                    weight += 0.5

            elif criteria == "lowest_cost":

                weight = edge_cost

            elif criteria == "least_transfers":

                # prioritize transfer count
                weight = (
                    1
                    if is_transfer
                    else 0
                )

                # tiny tie-breaker
                weight += edge_time * 0.001

            else:

                weight = edge_time

            new_g = g + weight

            state = (
                neighbor,
                neighbor_line_norm
            )

            # ==========================================
            # RELAXATION
            # ==========================================

            if (
                new_g
                < best_g.get(
                    state,
                    float('inf')
                )
            ):

                best_g[state] = new_g

                came_from[state] = (
                    current,
                    current_line_norm,
                    edge
                )

                h = heuristic(
                    neighbor,
                    end_nodes,
                    graph,
                    criteria
                )

                f_new = new_g + h

                heapq.heappush(
                    pq,
                    (
                        f_new,
                        next(counter),
                        new_g,
                        neighbor,
                        neighbor_line_norm,
                        next_time,
                        next_cost,
                        next_transfers
                    )
                )

    return {
        "status": "NO_ROUTE_FOUND"
    }


# =========================================================
# PATH RECONSTRUCTION
# =========================================================

def reconstruct_path(
        came_from,
        start_nodes,
        end_node,
        end_line,
        total_time,
        total_cost,
        total_transfers,
        graph
):

    current = end_node

    current_line = end_line

    path_edges = []

    # =====================================================
    # BACKTRACK
    # =====================================================

    while (
        current,
        current_line
    ) in came_from:

        prev, prev_line, edge_data = came_from[
            (current, current_line)
        ]

        path_edges.append(
            {
                "from": prev,
                "to": current,
                "line": edge_data.get("line"),
                "line_norm": normalize_line(
                    edge_data.get("line")
                ),
                "prev_line_norm": prev_line
            }
        )

        current = prev
        current_line = prev_line

    path_edges.reverse()

    # =====================================================
    # BUILD DETAILS
    # =====================================================

    path_stations = [current]

    details = []

    first_line = None

    for step in path_edges:

        normalized = normalize_line(
            step["line"]
        )

        if normalized is not None:
            first_line = normalized
            break

    details.append(
        {
            "station_id": current,
            "station_name":
                graph[current]["metadata"].get(
                    "name",
                    current
                ),
            "line": first_line,
            "action":
                "Board"
                if first_line
                else "Arrive",
            "coords": [
                graph[current]["metadata"].get("lat"),
                graph[current]["metadata"].get("lon")
            ]
        }
    )

    last_rail_line = first_line

    for i, step in enumerate(path_edges):

        path_stations.append(
            step["to"]
        )

        station_name = graph[
            step["to"]
        ]["metadata"].get(
            "name",
            step["to"]
        )

        is_last = (
            i == len(path_edges) - 1
        )

        current_line_raw = step["line"]

        current_line = step.get(
            "line_norm"
        )

        if is_last:

            action = "Arrive"

        elif current_line is None:

            action = "Continue"

        elif (
            last_rail_line is not None
            and current_line != last_rail_line
        ):

            action = "Transfer"

        else:

            action = "Continue"

        if current_line is not None:
            last_rail_line = current_line

        details.append(
            {
                "station_id": step["to"],
                "station_name": station_name,
                "line": current_line_raw,
                "action": action,
                "coords": [
                    graph[step["to"]]["metadata"].get("lat"),
                    graph[step["to"]]["metadata"].get("lon")
                ]
            }
        )

    return {
        "status": "SUCCESS",
        "route": {
            "path": path_stations,
            "total_time": round(total_time, 1),
            "total_cost": round(total_cost, 1),
            "transfers": total_transfers,
            "details": details
        }
    }
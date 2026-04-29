import heapq
import math
import itertools

def normalize_line(line):
    if not line:
        return None
    line = line.lower()
    if line == 'walk':
        return None
    # Remove common prefixes and suffixes
    line = line.replace('jr ', '').replace(' line', '').replace('line ', '').strip()
    return line


def calculate_haversine_km(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def heuristic(current, goals, graph, criteria):
    if current not in graph or not goals:
        return 0

    if not isinstance(goals, (list, set, tuple)):
        goals = [goals]

    lat1 = graph[current]["metadata"]["lat"]
    lon1 = graph[current]["metadata"]["lon"]

    best_heuristic = float('inf')
    for goal in goals:
        if goal not in graph:
            continue
        lat2 = graph[goal]["metadata"]["lat"]
        lon2 = graph[goal]["metadata"]["lon"]
        distance_km = calculate_haversine_km(lat1, lon1, lat2, lon2)

        if criteria == "shortest_time":
            best_heuristic = min(best_heuristic, distance_km * 1.0)
        elif criteria == "lowest_cost":
            best_heuristic = min(best_heuristic, distance_km * 10.0)
        elif criteria == "least_transfers":
            best_heuristic = min(best_heuristic, 0)
        else:
            best_heuristic = min(best_heuristic, distance_km)

    return best_heuristic if best_heuristic != float('inf') else 0


# ================= MAIN FUNCTION =================
def find_optimal_route(graph, start, end, criteria):
    start_nodes = [start] if isinstance(start, str) else list(start)
    end_nodes = [end] if isinstance(end, str) else list(end)

    start_nodes = [node for node in start_nodes if node in graph]
    end_nodes = [node for node in end_nodes if node in graph]

    if not start_nodes or not end_nodes:
        return {"status": "NO_ROUTE_FOUND"}

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
                    "details": [{
                        "station_id": start_node,
                        "station_name": graph[start_node]["metadata"].get("name", start_node),
                        "line": None,
                        "action": "Arrive"
                    }]
                }
            }

    pq = []
    counter = itertools.count()
    best_g = {}
    came_from = {}

    for start_node in start_nodes:
        h = heuristic(start_node, end_nodes, graph, criteria)
        heapq.heappush(pq, (h, next(counter), 0, start_node, None, 0, 0, 0))
        best_g[(start_node, None)] = 0

    while pq:
        f, _, g, current, current_line, curr_time, curr_cost, curr_transfers = heapq.heappop(pq)

        if current in end_set:
            return reconstruct_path(came_from, start_nodes, current, current_line, curr_time, curr_cost, curr_transfers, graph)

        if best_g.get((current, current_line), float('inf')) < g:
            continue

        current_line_norm = normalize_line(current_line)
        for neighbor, edge in graph[current]["connections"].items():
            neighbor_line_raw = edge.get("line")
            neighbor_line_norm = normalize_line(neighbor_line_raw)
            is_transfer = (
                current_line_norm is not None
                and neighbor_line_norm is not None
                and current_line_norm != neighbor_line_norm
            )

            next_time = curr_time + edge.get("time", 0)
            next_cost = curr_cost + edge.get("cost", 0)
            next_transfers = curr_transfers + (1 if is_transfer else 0)

            if criteria == "shortest_time":
                weight = edge.get("time", 0) + (3 if is_transfer else 0)
            elif criteria == "lowest_cost":
                weight = edge.get("cost", 0)
            elif criteria == "least_transfers":
                weight = 100 if is_transfer else 1
            else:
                weight = edge.get("time", 0)

            new_g = g + weight
            if new_g < best_g.get((neighbor, neighbor_line_norm), float('inf')):
                best_g[(neighbor, neighbor_line_norm)] = new_g
                came_from[(neighbor, neighbor_line_norm)] = (current, current_line_norm, edge)
                h = heuristic(neighbor, end_nodes, graph, criteria)
                f_new = new_g + h
                heapq.heappush(
                    pq,
                    (f_new, next(counter), new_g, neighbor, neighbor_line_norm, next_time, next_cost, next_transfers)
                )

    return {"status": "NO_ROUTE_FOUND"}


# ================= SUPPORT FUNCTIONS =================
def reconstruct_path(came_from, start_nodes, end_node, end_line, total_time, total_cost, total_transfers, graph):
    current = end_node
    current_line = end_line
    path_edges = []

    while (current, current_line) in came_from:
        prev, prev_line, edge_data = came_from[(current, current_line)]
        path_edges.append({
            "from": prev,
            "to": current,
            "line": edge_data.get("line"),
            "line_norm": normalize_line(edge_data.get("line")),
            "prev_line_norm": prev_line
        })
        current = prev
        current_line = prev_line

    path_edges.reverse()
    path_stations = [current]
    details = []

    first_line = None
    for step in path_edges:
        normalized = normalize_line(step["line"])
        if normalized is not None:
            first_line = normalized
            break

    if first_line is not None:
        details.append({
            "station_id": current,
            "station_name": graph[current]["metadata"].get("name", current),
            "line": first_line,
            "action": "Board",
            "coords": [
                graph[current]["metadata"].get("lat"),
                graph[current]["metadata"].get("lon")
            ]
        })
    else:
        details.append({
            "station_id": current,
            "station_name": graph[current]["metadata"].get("name", current),
            "line": None,
            "action": "Arrive",
            "coords": [
                graph[current]["metadata"].get("lat"),
                graph[current]["metadata"].get("lon")
            ]
        })

    last_rail_line = first_line
    for i, step in enumerate(path_edges):
        path_stations.append(step["to"])
        station_name = graph[step["to"]]["metadata"].get("name", step["to"])
        is_last = i == len(path_edges) - 1
        current_line_raw = step["line"]
        current_line = step.get("line_norm")

        if is_last:
            action = "Arrive"
        elif current_line is None:
            action = "Continue"
        elif last_rail_line is not None and current_line != last_rail_line:
            action = "Transfer"
        else:
            action = "Continue"

        if current_line is not None:
            last_rail_line = current_line

        details.append({
            "station_id": step["to"],
            "station_name": station_name,
            "line": current_line_raw,
            "action": action,
            "coords": [
                graph[step["to"]]["metadata"].get("lat"),
                graph[step["to"]]["metadata"].get("lon")
            ]
        })

    return {
        "status": "SUCCESS",
        "route": {
            "path": path_stations,
            "total_time": total_time,
            "total_cost": total_cost,
            "transfers": total_transfers,
            "details": details
        }
    }

import json
from typing import Any, List, Dict
from ..utils.logger import logger

def validate_stations_json(data: Any) -> List[str]:
    """
    Validate stations.json structure.
    Expected: List of dicts with 'id', 'title' (dict with 'en'/'ja'), 'coord' (list of 2 floats).
    Returns list of error messages.
    """
    errors = []
    if not isinstance(data, list):
        errors.append("Stations data must be a list.")
        return errors

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item {i} is not a dict.")
            continue
        if 'id' not in item:
            errors.append(f"Item {i} missing 'id'.")
        if 'title' not in item or not isinstance(item['title'], dict):
            errors.append(f"Item {i} missing or invalid 'title'.")
        else:
            title = item['title']
            if 'en' not in title and 'ja' not in title:
                errors.append(f"Item {i} 'title' missing 'en' or 'ja'.")
        if 'coord' not in item or not isinstance(item['coord'], list) or len(item['coord']) != 2:
            errors.append(f"Item {i} missing or invalid 'coord' (must be [lon, lat]).")
        else:
            try:
                float(item['coord'][0]), float(item['coord'][1])
            except ValueError:
                errors.append(f"Item {i} 'coord' values not floats.")
    return errors

def validate_railway_json(data: Any) -> List[str]:
    """
    Validate railway.json structure.
    Expected: List of dicts with 'id', 'title', 'stations' (list of str).
    """
    errors = []
    if not isinstance(data, list):
        errors.append("Railway data must be a list.")
        return errors

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item {i} is not a dict.")
            continue
        if 'id' not in item:
            errors.append(f"Item {i} missing 'id'.")
        if 'title' not in item or not isinstance(item['title'], dict):
            errors.append(f"Item {i} missing or invalid 'title'.")
        if 'stations' not in item or not isinstance(item['stations'], list):
            errors.append(f"Item {i} missing or invalid 'stations' (must be list of str).")
        else:
            for j, station in enumerate(item['stations']):
                if not isinstance(station, str):
                    errors.append(f"Item {i} station {j} is not str.")
    return errors

def validate_station_groups_json(data: Any) -> List[str]:
    """
    Validate station_groups.json structure.
    Expected: List of lists of lists of str (complex groups).
    """
    errors = []
    if not isinstance(data, list):
        errors.append("Station groups data must be a list.")
        return errors

    for i, group in enumerate(data):
        if not isinstance(group, list):
            errors.append(f"Group {i} is not a list.")
            continue
        for j, fare_zone in enumerate(group):
            if not isinstance(fare_zone, list):
                errors.append(f"Group {i} fare_zone {j} is not a list.")
                continue
            for k, station in enumerate(fare_zone):
                if not isinstance(station, str):
                    errors.append(f"Group {i} fare_zone {j} station {k} is not str.")
    return errors

def validate_json_file(file_path: str, validator_func) -> bool:
    """
    Load and validate a JSON file using the given validator function.
    Logs errors and returns True if valid.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        errors = validator_func(data)
        if errors:
            for error in errors:
                logger.error(f"Validation error in {file_path}: {error}")
            return False
        logger.info(f"{file_path} is valid.")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return False
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return False

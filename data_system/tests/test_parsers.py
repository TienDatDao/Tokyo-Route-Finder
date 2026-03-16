# Đảm bảo đọc JSON không bị sót trường hợp nào, đặc biệt là khi có trường hợp lỗi xảy ra
import unittest
import os
import sys

# Cấu hình đường dẫn tự động
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_SYSTEM_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(DATA_SYSTEM_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from data_system.core.parsers import parse_stations, parse_railway, parse_station_groups
from data_system.utils.validators import validate_stations_json, validate_railway_json, validate_station_groups_json, validate_json_file

class TestParsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_dir = os.path.join(DATA_SYSTEM_DIR, "raw_data")
        cls.stations_path = os.path.join(cls.raw_dir, "stations.json")
        cls.railway_path = os.path.join(cls.raw_dir, "railway.json")
        cls.groups_path = os.path.join(cls.raw_dir, "station_groups.json")

    def test_parse_stations(self):
        """Test parsing stations.json."""
        nodes = parse_stations(self.stations_path)
        self.assertIsInstance(nodes, dict)
        self.assertGreater(len(nodes), 0)
        # Check a sample node
        sample_id = next(iter(nodes.keys()))
        node = nodes[sample_id]
        self.assertIn('id', node.__dict__)
        self.assertIn('name', node.__dict__)
        self.assertIn('lat', node.__dict__)
        self.assertIn('lon', node.__dict__)

    def test_parse_railway(self):
        """Test parsing railway.json."""
        data = parse_railway(self.railway_path)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        # Check structure
        item = data[0]
        self.assertIn('id', item)
        self.assertIn('title', item)
        self.assertIn('stations', item)

    def test_parse_station_groups(self):
        """Test parsing station_groups.json."""
        data = parse_station_groups(self.groups_path)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        # Check nested structure
        self.assertIsInstance(data[0], list)

class TestValidators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "raw_data")
        cls.stations_path = os.path.join(cls.raw_dir, "stations.json")
        cls.railway_path = os.path.join(cls.raw_dir, "railway.json")
        cls.groups_path = os.path.join(cls.raw_dir, "station_groups.json")

    def test_validate_stations_json(self):
        """Test validation of stations.json (real data has missing coords, which is expected)."""
        import json
        with open(self.stations_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        errors = validate_stations_json(data)
        # Real data has missing coords, so expect errors
        self.assertGreater(len(errors), 0, "Should detect missing coords in real data")

    def test_validate_railway_json(self):
        """Test validation of railway.json."""
        import json
        with open(self.railway_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        errors = validate_railway_json(data)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")

    def test_validate_station_groups_json(self):
        """Test validation of station_groups.json."""
        import json
        with open(self.groups_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        errors = validate_station_groups_json(data)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")

    def test_validate_json_file(self):
        """Test validate_json_file function (stations has errors, others valid)."""
        # Stations has errors
        self.assertFalse(validate_json_file(self.stations_path, validate_stations_json))
        # Others valid
        self.assertTrue(validate_json_file(self.railway_path, validate_railway_json))
        self.assertTrue(validate_json_file(self.groups_path, validate_station_groups_json))

if __name__ == '__main__':
    unittest.main()

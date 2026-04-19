import json
import os


class StorageManager:
    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), "../../data")
        self.files = {
            "users": "users.json",
            "tables": "tables.json",
            "reservations": "reservations.json",
            "config": "restaurant_config.json",
        }

    def _load_file(self, file_key):
        """private method that helps read JSON data"""
        path = os.path.join(self.base_path, self.files[file_key])
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_file(self, file_key, data):
        """private method that helps write JSON data"""
        path = os.path.join(self.base_path, self.files[file_key])
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def load_tables(self):
        return self._load_file("tables")

    def load_reservations(self):
        return self._load_file("reservations")

    def save_reservations(self, reservation_data):
        all_reservations = self.load_reservations()
        all_reservations.append(reservation_data)
        self._save_file("reservations", all_reservations)

    def load_config(self):
        return self._load_file("config")

    def generate_next_id(self, file_key, prefix):
        data = self._load_file(file_key)
        counter = 1
        while True:
            candidate_id = f"{prefix}-{counter:}"
            found_match = False
            for item in data:
                if item["id"] == candidate_id:
                    found_match = True
                    break
            if not found_match:
                return candidate_id
            counter += 1

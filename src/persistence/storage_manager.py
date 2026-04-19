import json
import os
from src.utils.constants import (
    FILE_USERS,
    FILE_TABLES,
    FILE_RESERVATIONS,
    FILE_CONFIG,
    FLD_USER_ID,
)


class StorageManager:
    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), "../../data")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        self.files = {
            FILE_USERS: "users.json",
            FILE_TABLES: "tables.json",
            FILE_RESERVATIONS: "reservations.json",
            FILE_CONFIG: "restaurant_config.json",
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
        return self._load_file(FILE_TABLES)

    def load_reservations(self):
        return self._load_file(FILE_RESERVATIONS)

    def save_reservations(self, reservation_data):
        all_reservations = self.load_reservations()
        all_reservations.append(reservation_data)
        self._save_file(FILE_RESERVATIONS, all_reservations)

    def load_config(self):
        return self._load_file(FILE_CONFIG)

    def generate_next_id(self, file_key, prefix, id_field=FLD_USER_ID):
        data = self._load_file(file_key)
        counter = 1
        while True:
            candidate_id = f"{prefix}-{counter}"
            found_match = False
            for item in data:
                if item.get(id_field) == candidate_id:
                    found_match = True
                    break
            if not found_match:
                return candidate_id
            counter += 1

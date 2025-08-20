import json, os, time


class JSONCache:
    def __init__(self, file_name, ttl=300):
        self.file_name = file_name
        self.ttl = ttl

    def load(self):
        if not os.path.exists(self.file_name):
            return None

        with open(self.file_name, "r", encoding="utf-8") as f:
            cache = json.load(f)

        if time.time() - cache["timestamp"] > self.ttl:
            return None

        return cache["data"]

    def save(self, data):
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump({"data": data, "timestamp": time.time()}, f)

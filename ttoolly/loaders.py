import json


class JsonLoader:
    def __init__(self, path):
        with open(path) as f:
            self.data = json.loads(f.read())

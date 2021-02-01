import uuid


class Provider:
    def __init__(self):
        self._uid = str(uuid.uuid4())

    def get(self) -> str:
        return self._uid

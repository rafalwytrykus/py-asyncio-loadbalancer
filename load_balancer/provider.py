import uuid


class Provider:
    def __init__(self):
        self._uid = str(uuid.uuid4())

    async def get(self) -> str:
        return self._uid

    async def check(self) -> bool:
        return True

    def __hash__(self):
        return hash(self._uid)

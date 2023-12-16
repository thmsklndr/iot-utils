import redis

class RedisClient:
    def __init__(self, host: str, port: int = 6379):
        self._client = None
        self.host = host
        self.port = port

    @property
    def client(self):
        if self._client and not self._client.ping():
            try:
                self._client.close()
            finally:
                self._client = None

        if not self._client:
            self._client = redis.Redis(self.host, self.port, decode_responses=True)
        return self._client


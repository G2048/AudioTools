class RedisException(Exception):
    detail = "Redis Exception"


class ConnectionUnavailable(RedisException):
    detail = "Redis is not available"

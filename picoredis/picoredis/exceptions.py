# -*- coding: utf-8 -*-


class RedisError(Exception):
    """RESP error returned by the Redis server."""
    pass


class RedisTimeout(Exception):
    """Reply from the Redis server cannot be read within the timeout."""


class ParseError(Exception):
    """Invalid input while parsing RESP data."""
    pass


class IncompleteData(ParseError):
    """Incomplete input while parsing RESP data."""

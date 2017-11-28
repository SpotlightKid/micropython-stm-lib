# -*- coding: utf-8 -*-
"""REdis Serialization Protocol (RESP) data types handling."""

from .exceptions import ParseError, ParseError, RedisError


CRLF = "\r\n"
CRLFLEN = len(CRLF)


class ParseError(Exception):
    """Incomplete input while parsing RESP data."""


def encode_request(*args):
    """Pack a series of arguments into a RESP array of bulk string."""
    result = []
    result.append("*")
    result.append(str(len(args)))
    result.append(CRLF)
    
    for arg in args:
        result.append(encode_bulk_string(str('' if arg is None else arg)))

    return "".join(result)


def encode_bulk_string(s):
    if not s:
        return '$-1' + CRLF
    else:
        return '$' + str(len(s)) + CRLF + s + CRLF


def _decode(data, start=0):
    term = data[start]

    if term == "*":
        return parse_array(data, start)
    elif term == "$":
        return parse_bulk_string(data, start)
    elif term == "+":
        return parse_simple_string(data, start)
    elif term == "-":
        raise RedisError(*parse_error(data, start)[0])
    elif term == ":":
        return parse_integer(data, start)
    else:
        raise ParseError("Invalid header byte at pos {}.".format(start))


def decode(data, start=0):
    return _decode(data, start)[0]


def parse_stream(data, start=0):
    while start < len(data):
        res = _decode(data, start)
        obj, start = res
        yield obj, start


def parse_array(data, start=0):
    endcnt = data.find(CRLF, start + 1)

    if endcnt == -1:
        raise ParseError("Unterminated array element count after pos {}.".format(start + 1))

    try:
        count = int(data[start + 1:endcnt])
    except (ValueError, TypeError):
        raise ParseError("Invalid array element count at pos {} - {}.".format(start + 1, endcnt))

    start = endcnt + CRLFLEN

    if count == -1:
        return None, endcnt

    result = []
    
    for i in range(count):
        if start + 4 < len(data):
            obj, start = _decode(data, start)
            result.append(obj)
        else:
            raise ParseError("Unterminated array element at pos {}".format(start))
    
    return result, start


def parse_bulk_string(data, start=0):
    endlen = data.find(CRLF, start + 1)
    
    if endlen == -1:
        raise ParseError("Unterminated bulk string length after pos {}.".format(start + 1))
    
    try:
        length = int(data[start + 1:endlen])
    except (ValueError, TypeError):
        raise ParseError("Invalid bulk string length at pos {} - {}.".format(start + 1, endlen))
    
    if length == -1:
        return None, endlen + CRLFLEN
    else:
        end = endlen + CRLFLEN + length
        return data[endlen + CRLFLEN:end], end + CRLFLEN


def parse_simple_string(data, start=0):
    end = data.find(CRLF, start + 1)
    if end == -1:
        raise ParseError("Unterminated simple string after pos {}.".format(start + 1))
    return data[start + 1:end], end + CRLFLEN


def parse_error(data, start=0):
    end = data.find(CRLF, start + 1)
    if end == -1:
        raise ParseError("Unterminated error string after pos {}.".format(start + 1))
    return tuple(data[start + 1:end].split(None, 1)), end + CRLFLEN


def parse_integer(data, start=0):
    end = data.find(CRLF, start + 1)
    if end == -1:
        raise ParseError("Unterminated integer after pos {}.".format(start + 1))
    try:
        return int(data[start + 1:end]), end + CRLFLEN
    except:
        raise ParseError("Invalid integer at pos {} - {}.".format(start + 1, end))

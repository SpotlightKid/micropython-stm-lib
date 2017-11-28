#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from picoredis import protocol as p


CRLF = '\r\n'
GARBAGE = '§%$\r\n"%\n$/'
GLEN = len(GARBAGE)
MULTI_MESSAGE_STREAM = (
    '*3\r\n$3\r\nSET\r\n$15\r\nmemtier-8232902\r\n$2\r\nxx\r\n'
    '*3\r\n$3\r\nSET\r\n$15\r\nmemtier-8232902\r\n$2\r\nxx\r\n'
    '*3\r\n$3\r\nSET\r\n$15\r\nmemtier-7630684\r\n$3\r\nAAA\r\n'
)


def test_encode_request():
    assert p.encode_request("ping") == '*1\r\n$4\r\nping\r\n'
    assert p.encode_request("set", "foo", "bar") == (
        '*3\r\n$3\r\nset\r\n$3\r\nfoo\r\n$3\r\nbar\r\n')
    assert p.encode_request(42) == '*1\r\n$2\r\n42\r\n'
    assert p.encode_request(3.141) == '*1\r\n$5\r\n3.141\r\n'
    assert p.encode_request(None) == '*1\r\n$-1\r\n'


def test_decode():
    assert p.decode("+ping\r\n") == 'ping'
    assert p.decode(MULTI_MESSAGE_STREAM) == ["SET", "memtier-8232902", "xx"]


def test_decode_error():
    with pytest.raises(p.RedisError) as e:
        p.decode('-boom' + CRLF)

    assert e.value.args == ('boom',)

    with pytest.raises(p.RedisError) as e:
        p.decode('-boom shaka lakka' + CRLF)

    assert e.value.args == ('boom', 'shaka lakka')


def test_parse_stream():
    assert tuple(msg for msg, next in p.parse_stream(MULTI_MESSAGE_STREAM)) == (
        ["SET", "memtier-8232902", "xx"],
        ["SET", "memtier-8232902", "xx"],
        ["SET", "memtier-7630684", "AAA"]
    )


def test_parse_integer():
    assert p.parse_integer(':42' + CRLF)[0] == 42
    assert p.parse_integer(GARBAGE + ':42' + CRLF, GLEN)[0] == 42
    assert p.parse_integer(':42' + CRLF + GARBAGE)[0] == 42
    assert p.parse_integer(GARBAGE + ':42' + CRLF + GARBAGE, GLEN)[0] == 42

    with pytest.raises(p.ParseError) as e:
        p.parse_integer(':42')

    assert str(e.value) == "Unterminated integer after pos 1."

    with pytest.raises(p.ParseError) as e:
        p.parse_integer(':foo\r\n')

    assert str(e.value) == "Invalid integer at pos 1 - 4."


def test_parse_simple_string():
    assert p.parse_simple_string('+ping' + CRLF)[0] == 'ping'

    assert p.parse_simple_string(GARBAGE + '+ping' + CRLF, GLEN)[0] == 'ping'
    assert p.parse_simple_string('+ping' + CRLF + GARBAGE)[0] == 'ping'
    assert p.parse_simple_string(GARBAGE + '+ping' + CRLF + GARBAGE, GLEN)[0] == 'ping'

    with pytest.raises(p.ParseError) as e:
        p.parse_simple_string('+ping')

    assert str(e.value) == "Unterminated simple string after pos 1."


def test_parse_error():
    assert p.parse_error('-boom' + CRLF)[0] == ('boom',)
    assert p.parse_error(GARBAGE + '-boom' + CRLF, GLEN)[0] == ('boom',)
    assert p.parse_error('-boom' + CRLF + GARBAGE)[0] == ('boom',)
    assert p.parse_error(GARBAGE + '-boom' + CRLF + GARBAGE, GLEN)[0] == ('boom',)

    assert p.parse_error('-boom shaka lakka' + CRLF)[0] == ('boom', 'shaka lakka')
    assert p.parse_error(GARBAGE + '-boom shaka lakka' + CRLF, GLEN)[0] == ('boom', 'shaka lakka')
    assert p.parse_error('-boom shaka lakka' + CRLF + GARBAGE)[0] == ('boom', 'shaka lakka')
    assert p.parse_error(GARBAGE + '-boom shaka lakka' + CRLF + GARBAGE, GLEN)[0] == ('boom', 'shaka lakka')

    with pytest.raises(p.ParseError) as e:
        p.parse_error('-boom')

    assert str(e.value) == "Unterminated error string after pos 1."

    with pytest.raises(p.ParseError) as e:
        p.parse_error('-boom shaka lakka')

    assert str(e.value) == "Unterminated error string after pos 1."


def test_parse_bulk_string():
    assert p.parse_bulk_string('$12' + CRLF + 'hello world!' + CRLF)[0] == 'hello world!'
    assert p.parse_bulk_string('$14' + CRLF + 'hello\r\ngoodbye' + CRLF)[0] == 'hello\r\ngoodbye'
    assert p.parse_bulk_string('$-1' + CRLF)[0] is None
    assert p.parse_bulk_string(GARBAGE + '$-1' + CRLF, GLEN)[0] is None
    assert p.parse_bulk_string('$0' + CRLF + CRLF)[0] == ''
    assert p.parse_bulk_string(GARBAGE + '$12' + CRLF + 'hello world!' + CRLF, GLEN)[0] == 'hello world!'
    assert p.parse_bulk_string('$12' + CRLF + 'hello world!' + CRLF + GARBAGE)[0] == 'hello world!'
    assert p.parse_bulk_string(GARBAGE + '$12' + CRLF + 'hello world!' + CRLF + GARBAGE, GLEN)[0] == 'hello world!'

    with pytest.raises(p.ParseError) as e:
        p.parse_bulk_string('$14foo')

    assert str(e.value) == "Unterminated bulk string length after pos 1."

    with pytest.raises(p.ParseError) as e:
        p.parse_bulk_string('$foo\r\n')

    assert str(e.value) == "Invalid bulk string length at pos 1 - 4."

    with pytest.raises(p.ParseError) as e:
        p.parse_bulk_string('$1.5\r\n')

    assert str(e.value) == "Invalid bulk string length at pos 1 - 4."

    with pytest.raises(p.ParseError) as e:
        p.parse_bulk_string(GARBAGE + '$1.5\r\n', GLEN)

    assert str(e.value) == "Invalid bulk string length at pos 11 - 14."

    with pytest.raises(p.ParseError) as e:
        p.parse_bulk_string('$1.5\r\n' + GARBAGE)

    assert str(e.value) == "Invalid bulk string length at pos 1 - 4."

    with pytest.raises(p.ParseError) as e:
        p.parse_bulk_string('$14foo' + GARBAGE)

    assert str(e.value) == "Invalid bulk string length at pos 1 - 9."


def test_parse_array():
    assert p.parse_array('*3\r\n$3\r\nset\r\n$3\r\nfoo\r\n$3\r\nbar\r\n')[0] == ["set", "foo", "bar"]
    assert p.parse_array('*-1' + CRLF) is None


if __name__ == '__main__':
    pytest.main()

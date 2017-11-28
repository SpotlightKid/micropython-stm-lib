# -*- coding: utf-8 -*-
"""A very minimal Redis client library (not only) for MicroPython."""

import usocket as socket
import uselect


CRLF = "\r\n"


class RedisError(Exception):
    """RESP error returned by the Redis server."""
    pass


class RedisTimeout(Exception):
    """Reply from the Redis server cannot be read within the timeout."""


class ParseError(Exception):
    """Invalid input while parsing RESP data."""
    pass


def encode_request(*args):
    """Pack a series of arguments into a RESP array of bulk string."""
    result = ["*"]
    result.append(str(len(args)))
    result.append(CRLF)

    for arg in args:
        if arg is None:
            result.append('$-1' + CRLF)
        else:
            s = str(arg) 
            result.append('$' + str(len(s)) + CRLF + s + CRLF)

    return "".join(result)


class Redis:
    """A very minimal Redis client."""
    
    def __init__(self, host='127.0.0.1', port=6379, timeout=3000, debug=False):
        self.timeout = timeout
        self.debug = debug
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(socket.getaddrinfo(host, port)[0][-1])
        self.poller = uselect.poll()
        self.poller.register(self.sock, uselect.POLLIN)

    def do_cmd(self, cmd, *args):
        req = encode_request(cmd, *args)

        if self.debug:
            print("SEND: {!r}".format(req))

        self.sock.send(req.encode('utf-8'))
        return self.read_response()

    __call__ = do_cmd

    def __getattr__(self, name):
        return lambda *args: self.do_cmd(name, *args)

    def read_response(self):
        line = self.readuntil(lambda l: l[-2:] == b'\r\n')
        rtype = line[:1].decode('utf-8')

        if rtype == '+':
            return line[1:-2]
        elif rtype == '-':
            raise RedisError(*line[1:-2].decode('utf-8').split(None, 1))
        elif rtype == ':':
            return int(line[1:-2])
        elif rtype == '$':
            length = int(line[1:-2])

            if length == -1:
                return None

            return self.readuntil(lambda l: len(l) == length + 2)[:-2]
        elif rtype == '*':
            length = int(line[1:-2])

            if length == -1:
                return None

            return [self.read_response() for item in range(length)]
        else:
            raise ParseError("Invalid response header byte.")

    def readuntil(self, predicate):
        buf = b''
        while not predicate(buf):
            ready = self.poller.poll(self.timeout)
            if not ready:
                raise RedisTimeout("Error reading response from Redis server within timeout.")

            for obj, ev in ready:
                if obj is self.sock and not ev & (uselect.POLLHUP | uselect.POLLERR):
                    buf += self.sock.recv(1)
                    break
            else:
                raise OSError("Error reading from socket.")

        if self.debug:
            print("RECV: {!r}".format(buf))

        return buf

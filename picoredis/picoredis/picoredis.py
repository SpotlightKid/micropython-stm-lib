# -*- coding: utf-8 -*-
"""A very minimal Redis client library (not only) for MicroPython."""

try:
    import usocket as socket
except ImportError:
    import socket

try:
    import uselect as select
except ImportError:
    import select


CRLF = "\r\n"


class RedisError(Exception):
    """RESP error returned by the Redis server."""
    pass


class RedisTimeout(Exception):
    """Reply from the Redis server cannot be read within timeout."""


class ParseError(Exception):
    """Invalid input while parsing RESP data."""
    pass


def encode_request(*args):
    """Pack a series of arguments into a RESP array of bulk strings."""
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
        self._timeout = timeout
        self.debug = debug
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(socket.getaddrinfo(host, port)[0][-1])
        self._sock_fd = self._sock.makefile('rb').fileno()
        self._poller = select.poll()
        self._poller.register(self._sock_fd, select.POLLIN)

    def do_cmd(self, cmd, *args):
        req = encode_request(cmd, *args)

        if self.debug:
            print("SEND: {!r}".format(req))

        self._sock.send(req.encode('utf-8'))
        return self._read_response()

    __call__ = do_cmd

    def __getattr__(self, name):
        if name.isalpha() and not name.startswith('_'):
            return lambda *args: self.do_cmd(name, *args)
        raise AttributeError

    def _read_response(self):
        line = self._readuntil(lambda l, pos: l[-2:] == b'\r\n')
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

            return self._readuntil(lambda l, pos: pos == length + 2)[:-2]
        elif rtype == '*':
            length = int(line[1:-2])

            if length == -1:
                return None

            return [self._read_response() for item in range(length)]
        else:
            raise ParseError("Invalid response header byte.")

    def _readuntil(self, predicate):
        buf = b''
        pos = 0
        while not predicate(buf, pos):
            ready = self._poller.poll(self._timeout)
            if not ready:
                raise RedisTimeout("Error reading response from Redis server within timeout.")

            for fd, ev in ready:
                if (fd == self._sock_fd and ev & select.POLLIN and not
                        ev & (select.POLLHUP | select.POLLERR)):
                    buf += self._sock.recv(1)
                    pos += 1
                    break
            else:
                raise OSError("Error reading from socket.")

        if self.debug:
            print("RECV: {!r}".format(buf))

        return buf

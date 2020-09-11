import usocket


MAX_READ_SIZE = 4*1024


def encode_basic_auth(user, password):
    from ubinascii import b2a_base64
    auth_encoded = b2a_base64(b"%s:%s" % (user, password)).rstrip(b'\n')
    return {b'Authorization': b'Basic %s' % auth_encoded}


def head(url, **kw):
    return request("HEAD", url, **kw)


def get(url, **kw):
    return request("GET", url, **kw)


def post(url, **kw):
    return request("POST", url, **kw)


def put(url, **kw):
    return request("PUT", url, **kw)


def patch(url, **kw):
    return request("PATCH", url, **kw)


def delete(url, **kw):
    return request("DELETE", url, **kw)


class Response:
    def __init__(self, f, save_headers=False):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None
        self._chunk_size = 0
        self._content_size = 0
        self.chunked = False
        self.status = None
        self.reason = ""
        self.headers = [] if save_headers else None

    def read(self, size=MAX_READ_SIZE):
        if self.chunked:
            if self._chunk_size == 0:
                l = self.raw.readline()
                #print("chunk line:", l)
                l = l.split(b";", 1)[0]
                self._chunk_size = int(l, 16)
                #print("chunk size:", self._chunk_size)

                if self._chunk_size == 0:
                    # End of message
                    sep = self.raw.read(2)
                    if sep != b"\r\n":
                        raise ValueError("Expected final chunk separator, read %r instead" % sep)

                    return b''

            data = self.raw.read(min(size, self._chunk_size))
            self._chunk_size -= len(data)

            if self._chunk_size == 0:
                sep = self.raw.read(2)
                if sep != b"\r\n":
                    raise ValueError("Expected chunk separator, read %r instead" % sep)

            return data
        else:
            if size:
                return self.raw.read(size)
            else:
                return self.raw.read(self._content_size)

    def save(self, fn, chunk_size=1024):
        read = 0

        with open(fn, 'wb') as fp:
            while True:
                remain = self._content_size - read

                if remain == 0:
                    break

                chunk = self.read(min(chunk_size, remain))
                read += len(chunk)

                if not chunk:
                    break

                fp.write(chunk)

        self.close()


    def add_header(self, line):
        if line[:18].lower() == b"transfer-encoding:" and b"chunked" in line:
            self.chunked = True
        elif line[:15].lower() == b"content-length:":
            self._content_size = int(line.split(b':', 1)[1])

        if self.headers is not None:
            self.headers.append(line)

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.read(size=None)
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


def request(method, url, data=None, json=None, headers={}, auth=None, stream=None,
            response_class=Response, save_headers=False):
    if auth:
        headers.update(auth if callable(auth) else encode_basic_auth(auth[0], auth[1]))

    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""

    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    s = usocket.socket(ai[0], ai[1], ai[2])
    try:
        s.connect(ai[-1])
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)

        s.write(b"%s /%s HTTP/1.1\r\n" % (method.encode(), path.encode('utf-8')))

        if not b"Host" in headers:
            s.write(b"Host: %s\r\n" % host.encode())

        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")

        if json is not None:
            assert data is None
            import ujson
            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")

        if data:
            s.write(b"Content-Length: %d\r\n" % len(data))

        s.write(b"\r\n")

        if data:
            s.write(data)

        resp = response_class(s, save_headers=save_headers)
        l = b""; i = 0
        while True:
            l += s.read(1)
            i += 1

            if l.endswith(b'\r\n') or i > MAX_READ_SIZE:
                break

        #print("Response: ", l)
        l = l.split(None, 2)
        resp.status = int(l[1])

        if len(l) > 2:
            resp.reason = l[2].rstrip()

        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break

            if l.startswith(b"Location:") and not 200 <= status <= 299:
                raise NotImplementedError("Redirects not yet supported")

            #print("Header: %r" % l)
            resp.add_header(l)
    except OSError:
        s.close()
        raise

    return resp

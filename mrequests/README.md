# mrequests

A HTTP client module for MicroPython with an API *similar* to [requests].

This is an evolution of the [urequests] module from [micropython-lib] with a few
extensions and many fixes and convenience features.


## Features & Limitations

### Features

* Supports redirection with absolute and relative URLs (see below for details).
* Supports HTTP basic authentication (requires `ubinascii` module).
* Supports socket timeouts.
* Response headers can optionally be saved in the response object.
* Respects `Content-length` header in response.
* Supports responses with chunked transfer encoding.
* `Response` objects have a `save` method to save the response body to
  a file, reading the response data and writing the file in small chunks.
* The `Response` class for response objects can be substituted by a custom
  response class.


### Limitations

- `mrequests.request` is a synchroneous, blocking function.
- The code is *not* interrupt save and a fair amount of memory allocation is
  happening in the process of handling a request.
- URL parsing does not cover all corner cases (see [test_urlparse] for details).
- URLs with authentication credentials in the host part (e.g.
  `http://user:secret@myhost/`) are *not supported*. Pass authentication
  credentials separately via the `auth` argument instead.
- SSL/TLS support on the MicroPython *unix*, *stm32* and *esp8266* ports is
  limited. In particular their `ssl` module does not support all encryption
  schemes commonly in use by popular servers, meaning that trying to connect
  to them via HTTPS will fail with various cryptic error messages.
- Request and JSON data may be passed in as bytes or strings and the request
  data will be encoded to bytes, if necessary, using the encoding given with
  the `encoding` parameter. But be aware that encodings other than `utf-8` are
  *not supported* by most (any?) MicroPython implementations.
- Custom headers may be passed as a dictionary with string or bytes keys and
  values and must contain only ASCII chars. If you need header values to use
  non-ASCII chars, you need to encode them according to RFC 8187.
- The URL and specifically any query string parameters it contains will not be
  URL-encoded, and it may contain only ASCII chars. Make sure you encode the
  query string part of the URL with `urlencode.quote` before passing it, if
  necessary.
- When encoding `str` instances via `urlencode.urlencode` or `urlencode.quote`,
  the `encoding` and `errors` arguments are currently ignored by MicroPython and
  it behaves as if their values were `"utf-8"` resp. `"ignore"`.


### Redirection Support

* Can follow redirects for response status codes 301, 302, 303, 307 and 308.
* The HTTP method is changed to `GET` for redirects, unless the original
  method was `HEAD` or the status code is 307 or 308.
* For status code 303, if the method of the request resulting in a redirection
  (which may have been the result of a previous redirection) is `GET`, the
  redirection is not followed, since the `Location` header is supposed to
  indicate a non-HTTP resource then.
* Redirects are allowed to change the protocol from `http` to `https`,
  but redirects changing from `https` to `http` will not be followed.
* The `request` function has an additional keyword argument `max_redirects`,
  defaulting to 1, which controls how many level of redirections are followed.
  If this is exceeded, the function raises a `ValueError`.
* The code does not check for infinite redirection cycles. It is advised to
  keep `max_redirects` to a low number instead.


## Installation

Make sure you have `mpy-cross` and `rshell` installed and in your shell's
`PATH`.

For boards with the `stm32` port:

    DESTDIR=/flash ./install.sh

For boards with the `esp8266` or `esp32` port:

    DESTDIR=/pyboard PORT=/dev/ttyUSB0 BAUD=115200 ./install.sh

This will compile the Python modules with `mpy-cross` and copy the resulting
`.mpy` files to the board's flash.

For the `unix` port, just copy all the `.py` files in the root of the
repository to a directory, which is in `sys.path`, e.g. `~/.micropython/lib`
of or set the `MICROPYPATH` environment variable to a colon-separated list of
directories including the one to which you copied the modules.

Note: the `mrequests.py` module has no dependencies besides modules usually
already built in to the MicroPython firmware on all ports (as of version 1.15)
and can be installed and used on its own. `defaultdict.py` and `urlencode.py`
provide support for sending form-encoded request parameters or data (see the
`formencode.py` script in the `examples` directory for an example of their
use).


## Examples

See the scripts in the [examples](./examples) directory for more.

### Simple GET request with JSON response

```py
>>> import mrequests as requests
>>> r = requests.get("http://httpbin.org/get",
                     headers={"Accept": "application/json"})
>>> print(r)
<Response object at 7f6f91631be0>
>>> print(r.content)
b'{\n  "args": {}, \n  "headers": {\n    "Accept": "application/json", \n
"Host": "httpbin.org", \n    "X-Amzn-Trace-Id": "Root=1-[redacted]"\n  }, \n
"origin": "[redacted]", \n  "url": "http://httpbin.org/get"\n}\n'
>>> print(r.text)
{
  "args": {},
  "headers": {
    "Accept": "application/json",
    "Host": "httpbin.org",
    "X-Amzn-Trace-Id": "Root=1-[redacted]"
  },
  "origin": "[redacted]",
  "url": "http://httpbin.org/get"
}

>>> print(r.json())
{'url': 'http://httpbin.org/get', 'headers': {'X-Amzn-Trace-Id':
'Root=1-[redacted]', 'Host': 'httpbin.org', 'Accept': 'application/json'},
'args': {}, 'origin': '[redacted]'}
>>> r.close()
```

It is mandatory to close response objects as soon as you finished working with
them. On MicroPython platforms without full-fledged OS, not doing so may lead
to resource leaks and malfunction.


### HTTP Basic Auth

```py
>>> import mrequests as requests
>>> user = "joedoe"
>>> password = "simsalabim"
>>> url = "http://httpbin.org/basic-auth/%s/%s" % (user, password)
>>> r = requests.get(url, auth=(user, password))
>>> print(r.text)
{
  "authenticated": true,
  "user": "joedoe"
}
>>> r.close()
```

[micropython-lib]: https://github.com/micropython/micropython-lib
[requests]: https://github.com/psf/requests
[test_urlparse]: ./tests/test_urlparse.py
[urequests]: https://github.com/micropython/micropython-lib/blob/master/urequests/urequests.py

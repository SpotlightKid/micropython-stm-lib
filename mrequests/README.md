# mrequests

A HTTP client module for MicroPython with an API *similar* to [requests].

This is an evolution of the [urequests] module from [micropython-lib] with a few
extensions and many fixes and convenience features.


## Features & Limitations


### Compatibility

Supports the unix, stm32, esp8266 and esp32 MicroPython ports as well as
CPython.

On the unix, stm32 and esp8266 ports the SSL/TLS support has some limitations
due to problems with MicroPython's `ssl` module on these platforms.

On the stm32 port installing a custom-compiled firmware with network/SSL
support is required.


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


## Reference

The main function provided by `mrequests` is `requests`, which takes an HTTP
method and a URL as positional arguments and several optional keyword arguments
and returns a `Response` object:

```py
request(method, url, data=None, json=None, headers={}, auth=None,
        encoding=None, response_class=Response, save_headers=False,
        max_redirects=1, timeout=None)
```

Parameters:

*method (str)* - the HTTP method as a string in all-caps.

*url (str)* - the URL of the request as a string. This must be an absolute URL,
including the protocol (only `http://` and `https://` are supported) and a host
name or IP address. The server name may be suffixed with a port number,
separated by a colon. The default port is 80 for `http` URLs and 443 for
`https`.

Authentication credentials in the host part are not supported (see the *auth*
parameter below).

The URL may contain only ASCII chars. The caller is responsible for encoding
any non-ASCII chars in the path or the query string (for example with
`urlencode.quote`) or encoding IDN host names if necessary.

*data (bytes, str)* - the request body data as `bytes` or `str` instance. If
given as a string, it will be converted to `bytes` using the encoding given
with the `encoding` parameter (requiring additional memory to allocate the new
bytes object). The caller is responsible for formatting the request data
according to the content type specified in the request headers.

*json (obj)* - an object, which will be encoded as JSON and sent as the request
body data. Also adds a `Content-Type` header with the value `application/json`.
This overwrites data passed with the *data* parameter and allocates memory for
the request data. To avoid allocation, pass a JSON-encoded byte string with the
*data* parameter instead.

*headers (dict)* - a dictionary of additional request headers to sent. Keys and
values can by `bytes` or `str` instances and may contain only ASCII chars.
`str` keys and values will be converted to `bytes` using the encoding given
with the `encoding` parameter, which causes memory allocation.

A `Content-Length` header will always be added, using the length of the request
data as the value. If no `Host` header was passed, one will be added, using the
host name from the URL as the value.

*auth (tuple)* - HTTP basic authentication credentials given as a
`(user, password)` tuple of `bytes` objects or a callable, returning such a
tuple. Some MicroPython versions may also accept `str` instances as the tuple
elements but may issue a warning message. This will overwrite `Authorization`
headers passed in with the *headers* parameter.

*encoding (str)* - the encoding of the request body data, if the the data is
passed in as a `str` instance with the *data* or *json* parameters. Defauts to
`utf-8`.

*response_class (obj)* - the class to use for the returned response objects.
Defaults to `mrequests.Response`. Custom response classes should sub-class
`mrequests.Response` and must take the same constructor arguments.

*save_headers (bool)* - a boolean, which is passed to the constructor of the
response class instance, which determines whether it keeps a refernce to the
response headers in the instance. This is set to `False` by default to save
memory. If set to `True`, the default response class will make the reponse
header lines available via its `headers` instance attribute as a list of
unparsed `bytes` objects.

*max_redirects (int)* - the maximum number of valid redirections to follow.
Defaults to 1. If too many redirections are encountered, a `ValueError` is
raised.

*timeout (float)* - sets the timeout for the connection socket as a
non-negative float in seconds. Defaults to `None`, which blocks indefinitely.
If a non-zero value is given, connection attempts or socket read/write
operations will raise `OSError` if the timeout period value has elapsed before
the operation has completed. If zero is given, the socket is put in
non-blocking mode.

---

Several convenience wrappers for creating request using common HTTP methods are
available:

```py
head(url, **kw)

get(url, **kw)

post(url, **kw)

put(url, **kw)

patch(url, **kw)

delete(url, **kw)
```

The url and all keyword arguments are simply passed to `request`.

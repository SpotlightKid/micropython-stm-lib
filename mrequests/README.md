# mrequests

This is an evolution of the [urequests] module from [micropython-lib] with a few
extensions:


## Features

* Supports redirection with absolute and relative URLs (see below for details).
* Response headers can optionally be saved in the response object.
* The `Response` class for response objects can be substituted by a custom
  response class.
* Support for HTTP basic auth (requires `ubinascii` module).
* Support for responses with chunked transfer encoding.
* Respects `Content-length` header in response.
* `Response` objects have a `save` method to save the response body to
  a file, reading the response data and writing the file in small chunks.

Otherwise the API remains the same.


### Redirection Support

* Can follow redirects for response status codes 301, 302, 303, 307 and 308.
* The HTTP method is changed to `GET` for redirects, unless the original
  method was `HEAD` or the status code is 307 or 308.
* For status code 303, if the original method is `GET`, the redirection is not
  followed, since the `Location` header is supposed to indicate a non-HTTP
  resource then.
* Redirects are allowed to change the protocol from `http` to `https`,
  but redirects changing from `https` to `http` will not be followed.
* The `request` function has an additional keyword argument `max_redirects`,
  defaulting to 1, which controls how many level of redirections are followed.
  If this is exceeded, the function raises a `ValueError`.
* The code does not check for infinite redirection cycles. It is advised to
  keep `max_redirects` to a low number instead.


## Examples


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
[urequests]: https://github.com/micropython/micropython-lib/blob/master/urequests/urequests.py

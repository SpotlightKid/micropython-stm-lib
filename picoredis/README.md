PicoRedis
=========

## Overview

`picoredis`  is a very minimal Redis client (not only)  for MicroPython.

### What is does

* Support the **RE**dis **S**erialization **P**rotocol
  ([RESP](https://redis.io/topics/protocol)).
* Connect to a Redis server via TCP.
* Send [Redis commands](https://redis.io/topics/protocol) and receive and parse
  the response in a simple, blocking fashion.
* Support MicroPython (unix and bare-metal ports with `usocket` and `uselect`
  module), CPython and PyPy (3.4+, 2.7+ untested).

### What it does not

* Parse the response beyond de-serialization of the basic RESP types
  (`simple string`, `error`, `bulk string`, `integer` and `array`).
* Decode response byte strings, except error messages.
* Support the subscribe / publish protocol.
* Support SSL / TLS (yet).
* Async I/O.

## Usage

```
#!python
>>> from picoredis import Redis
>>> redis = Redis()  # server defaults to 127.0.0.1 port 6379
>>> redis.do_cmd('PING', 'Hello World!')
b'Hello World!'
```

Instead of using the `do_cmd` method, `Redis` instances can be called directly:

```
#!python
redis('SET', 'foo', 'bar')
b'OK'
redis('GET', 'foo')
b'bar'  # string responses are always byte strings
```

Or you can call arbitrary methods on the `Redis` instance, and the method name
will be used as the Redis command:

```
#!python
>>> redis.hset('myhash', 'key1', 42)
1
>>> redis.hkeys('myhash')
[b'key1']
```

You can use any alphanumeric method name without a leading underscore, except
`debug` and `do_cmd`, which are already used as an instance attribute resp.
method name. If the name does not correspond to a valid Redis command, the
server will return an error and a `RedisError` exception will be raised:

```
#!python
>>> redis.bogus('spam!')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "picoredis.py", line 72, in <lambda>
  File "picoredis.py", line 66, in do_cmd
  File "picoredis.py", line 82, in _read_response
RedisError: ('ERR', "unknown command 'bogus'")
```


### Connection Parameters

You can set the host name or IP address and port number of the Redis server to
connect to when creating an instance with the `host` and `port` keyword
arguments:

```
#!python
>>> redis = Redis('192.168.1.100')
>>> redis = Redis(port=6380)
>>> redis = Redis('192.168.1.100', 6380)
>>> redis = Redis(server='192.168.1.100')
>>> redis = Redis(server='192.168.1.100', port=6380)
```

You can set the TCP socket timeout with the `timeout` keyword argument in
milliseconds (default 3000):

```
#!python
>>> redis = Redis(timeout=10000)
```

If a response is read from the server and the server doesn't return any data
within the timeout, a `RedisTimeout` exception is raised.

### Debug Output

To turn on printing of raw messages sent to and received from the Redis server
pass `debug=True` when creating the instance or set its `debug` attribute to
`True`:

```
#!python
>>> redis = Redis(debug=True)
>>> redis.hkeys('myhash')
SEND: '*2\r\n$5\r\nhkeys\r\n$6\r\nmyhash\r\n'
RECV: b'*1\r\n'
RECV: b'$4\r\n'
RECV: b'key1\r\n'
[b'key1']
```


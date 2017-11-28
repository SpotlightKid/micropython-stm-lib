PicoRedis
=========


## Overview

**PicoRedis** is a very minimal Redis client (not only) for MicroPython.


### What is does

* Support the **RE**dis **S**erialization **P**rotocol ([RESP]).
* Connect to a Redis server via TCP.
* Send [Redis commands] and receive and parse the response in a simple,
  blocking fashion.
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

You can use any method name consisting of *only* letters, except `connect`,
`close`, `debug` (and `do_cmd`), which are already used as instance attribute
or method names. If the name does not correspond to a valid Redis command, the
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


### Connection

When you create a `Redis` instance, it immediatly tries to open a connecting to
the Redis server. The default host and port are `127.0.0.1` and `6379`
respectively.

You can set the host name or IP address and port number of the Redis server to
connect with the `host` and `port` keyword arguments:

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

To close the connection to the server, use the `close()` method:

```
#!python
>>> redis.close()
>>> redis.ping()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "picoredis.py", line 89, in <lambda>
  File "picoredis.py", line 75, in do_cmd
RedisError: Not connected: use 'connect()' to connect to Redis server.
```

To open a new connection again, use the `connect` method. You can pass a
different host name and / or port number and they will overwrite the ones given
when the instance was created:

```
#!python
>>> redis.connect('redis.myserver.com')
>>> redis._host
'redis.myserver.com'
```


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


### Tips

If you need to further parse the response to a Redis command regularly, just
add a wrapper method in a sub-class. For example, here is how to get the list
of commands supported by the Redis server as a list of strings:

```
#!python
>>> class MyRedis(Redis):
...     def command_list(self):
...         return sorted([cmd[0].decode('utf-8')
...                        for cmd in self.do_cmd('command')])
>>> redis = MyRedis()
>>> redis.command_list()
['append', 'asking', 'auth', 'bgrewriteaof', 'bgsave', 'bitcount', 'bitfield',
 ..., 'zunionstore']
```

**Warning:** The response to this command sent be the Redis server will be
fairly big and probably cause a `MemoryError`, when you run it on a
memory-constrained device like an ESP8266-based board.


## Installation

On CPython and PyPy use `pip` to install as usual:

    $ pip install picoredis

On the MicroPython unix port, use the `upip`:

    $ micropyton -m upip install picoredis

On MicroPython base-metal ports (*esp8266*, *stm32*, *wipy*, etc.), just
download the [picoredis.py] file from the repository and upload it to the flash
storage of your MicroPython board, e.g. using [ampy]:

    $ curl -O https://raw.githubusercontent.com/SpotlightKid/micropython-stm-lib/master/picoredis/picoredis/picoredis.py
    $ ampy -p /dev/ttyUSB0 put picoredis.py

You can also compile the `picoredis.py` module with [mpy-cross] and use it the
resulting `picoredis.mpy` file as a drop-in replacement for the pure Python
version. This will save you a good bit of memory on your MicroPython board,
because the byte-code compilation step, that normally happens when you import
the module, can be skipped:

    $ mpy-cross picoredis.py
    $ ampy -p /dev/ttyUSB0 put picoredis.mpy


## License

**PicoRedis** was written and is copyrighted by Christopher Arndt, 2017.

It is distributed under the terms of the `MIT license`_, **PicoRedis** is free
and open source software.


## Acknowledgements

Some inspiration and code ideas where taken from these projects:

* [redis_protocol] by Young King
* [micropython-redis] by Dwight Hubbard


[ampy]: https://github.com/adafruit/ampy
[micropython-redis]: https://github.com/dwighthubbard/micropython-redis
[mpy-cross]: https://github.com/micropython/micropython/tree/master/mpy-cross
[picoredis.py]: https://github.com/SpotlightKid/micropython-stm-lib/blob/master/picoredis/picoredis/picoredis.py
[redis commands]: https://redis.io/commands
[redis_protocol]: https://github.com/wayhome/redis_protocol
[resp]: https://redis.io/topics/protocol

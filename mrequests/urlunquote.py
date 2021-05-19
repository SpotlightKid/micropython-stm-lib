def unquote(string):
    """Decode and replace URL percent-escapes in string.

        unquote('abc%20def') -> b'abc def'.

    Note: If a string, not a bytes object, is passed, it is encoded as UTF-8.
    This is only an issue if it contains unescaped non-ASCII characters, which
    URIs should not.

    """
    if not string:
        return b''

    if isinstance(string, str):
        string = string.encode('utf-8')

    bits = string.split(b'%')
    if len(bits) == 1:
        return string

    res = bytearray(bits[0])
    append = res.append
    extend = res.extend

    for item in bits[1:]:
        try:
            append(int(item[:2], 16))
            extend(item[2:])
        except KeyError:
            append(b'%')
            extend(item)

    return bytes(res)

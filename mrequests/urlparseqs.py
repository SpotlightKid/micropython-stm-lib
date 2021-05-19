from urlunquote import unquote


def parse_qsl(
    qs,
    keep_blank_values=False,
    strict_parsing=False,
    encoding="utf-8",
    errors="replace",
    max_num_fields=None,
    separator=b"&",
):
    """Parse a query given as a bytes or string argument.

    Arguments:

    qs: percent-encoded query string to be parsed. May be a unicode
        string or a UTF-8 encoded byte-string.

    keep_blank_values: flag indicating whether blank values in
        percent-encoded queries should be treated as blank strings.
        A true value indicates that blanks should be retained as blank
        strings. The default false value indicates that blank values
        are to be ignored and treated as if they were not included.

    strict_parsing: flag indicating what to do with parsing errors. If
        false (the default), errors are silently ignored. If true,
        errors raise a ValueError exception.

    encoding: specify how to decode percent-encoded sequences into Unicode
        characters.

    separator: the symbol to use for separating the query arguments.
        It defaults to b'&'.

    Returns a list of (name, value) tuples.

    """
    if isinstance(qs, str):
        qs = qs.encode("utf-8")

    res = []

    if max_num_fields is not None and qs.count(separator) + 1 > max_num_fields:
        raise ValueError("'Max number of fields exceeded.")

    for field in qs.split(separator):
        if not field and not strict_parsing:
            continue

        nv = field.split(b"=", 1)

        if len(nv) != 2:
            if strict_parsing:
                raise ValueError("bad query field: {}".format(field))
            # Handle case of a field with no equal sign
            if keep_blank_values:
                nv.append(b"")
            else:
                continue

        if nv[1] or keep_blank_values:
            res.append(
                (
                    unquote(nv[0].replace(b"+", b" ")).decode(encoding, errors),
                    unquote(nv[1].replace(b"+", b" ")).decode(encoding, errors),
                )
            )

    return res


if __name__ == "__main__":
    url = "power=10&time=0.7&long+name+with+spaces=value%20with%20%C3%BCTF-8"

    for name, val in parse_qsl(url):
        print("%s: %s" % (name, val))

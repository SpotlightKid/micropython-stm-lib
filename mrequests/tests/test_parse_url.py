from unittest import TestCase, main

from mrequests import parse_url


TEST_CASES = [
    ("http://host:8888/foo/bar#spamm", ('http', 'host', 8888, "/foo/bar#spamm")),
    ("//host:8888/foo/bar#spamm", (None, 'host', 8888, "/foo/bar#spamm")),
    ("//host/foo/bar#spamm", (None, 'host', None, "/foo/bar#spamm")),
    ("/foo/bar#spamm", (None, None, None, "/foo/bar#spamm")),
    ("/foo#spamm", (None, None, None, '/foo#spamm')),
    ("http://host/", ("http", "host", None, '/')),
    ("http://host", ("http:", "host", None, '/')),
]


class TestUrlParse(TestCase):

    def test_url_parse(self):
        for url, expected in TEST_CASES:
            self.assertEqual(parse_url(url), expected)


if __name__ == '__main__':
    main()

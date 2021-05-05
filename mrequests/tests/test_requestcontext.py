from unittest import TestCase, main

from mrequests import RequestContext


TEST_DATA_SET_LOCATION = [
    (
        ("GET", "http://host/foo/index", 301, "new"),
        ("GET", "http://host/foo/new", True)
    ),
    (
        ("GET", "http://host/foo/index", 302, "new"),
        ("GET", "http://host/foo/new", True)
    ),
    (
        ("GET", "http://host/foo/index", 307, "new"),
        ("GET", "http://host/foo/new", True)
    ),
    (
        ("GET", "http://host/foo/index", 308, "new"),
        ("GET", "http://host/foo/new", True)
    ),
    (
        ("GET", "http://host/foo/index", 301, "/new"),
        ("GET", "http://host/new", True)
    ),
    (
        ("GET", "http://host/", 301, "http://otherhost"),
        ("GET", "http://otherhost/", True)
    ),
    (
        ("GET", "http://host/", 301, "http://host:8888"),
        ("GET", "http://host:8888/", True)
    ),
    (
        ("GET", "http://host:8888/", 301, "http://host/"),
        ("GET", "http://host/", True)
    ),
    (
        ("GET", "http://host/", 301, "https://host/"),
        ("GET", "https://host/", True)
    ),
    (
        ("GET", "http://host/", 301, "//otherhost/"),
        ("GET", "http://otherhost/", True)
    ),
    (
        ("GET", "https://host/", 301, "http://host/"),
        ("GET", "https://host/", False)
    ),
    (
       ("POST", "http://host/", 301, "/new"),
       ("GET", "http://host/new", True)
    ),
    (
       ("HEAD", "http://host/", 301, "/new"),
       ("HEAD", "http://host/new", True)
    ),
    (
       ("POST", "http://host/", 302, "/new"),
       ("GET", "http://host/new", True)
    ),
    (
       ("POST", "http://host/", 303, "/new"),
       ("GET", "http://host/new", True)
    ),
    (
       ("GET", "http://host/", 303, "non-HTTP location"),
       ("GET", "http://host/", False)
    ),
    (
       ("HEAD", "http://host/", 303, "/new"),
       ("HEAD", "http://host/new", True)
    ),
    (
       ("POST", "http://host/", 307, "/new"),
       ("POST", "http://host/new", True)
    ),
    (
       ("POST", "http://host/", 308, "/new"),
       ("POST", "http://host/new", True)
    ),
]

TEST_DATA_PORT = [
    ("http://host/", "http://host/", 80),
    ("http://host:80/", "http://host:80/", 80),
    ("https://host/", "https://host/", 443),
    ("https://host:443/", "https://host:443/", 443),
    ("http://host:8888/", "http://host:8888/", 8888),
    ("https://host:8888/", "https://host:8888/", 8888),
]


class TestRequestContext(TestCase):

    def test_set_location(self):
        for (method, url, status, location), (emethod, eurl, eredirect) in TEST_DATA_SET_LOCATION:
            rc = RequestContext(url, method)
            rc.set_location(status, location)
            self.assertEqual(rc.url, eurl)
            self.assertEqual(rc.method, emethod)
            self.assertEqual(rc.redirect, eredirect)

    def test_port(self):
        for url, eurl, eport in TEST_DATA_PORT:
            rc = RequestContext(url)
            self.assertEqual(rc.url, eurl)
            self.assertEqual(rc.port, eport)

        rc = RequestContext("http://host/")
        self.assertEqual(rc.port, 80)
        rc = RequestContext("http://host/")
        rc._port = 8000
        self.assertEqual(rc.port, 8000)
        rc = RequestContext("http://host:8000/")
        rc._port = None
        self.assertEqual(rc.port, 80)
        rc.scheme = "https"
        self.assertEqual(rc.port, 443)


if __name__ == '__main__':
    main()

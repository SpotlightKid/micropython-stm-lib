import mrequests


def request(method, url, data=None, json=None, headers=None):
    if isinstance(data, dict):
        from urlencode import urlencode

        data = urlencode(data)
        headers = {} if headers is None else headers
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    return mrequests.request(method, url, data=data, json=json, headers=headers)


if __name__ == "__main__":
    import sys

    url = "http://httpbin.org/post"
    data = dict((arg.split("=") for arg in sys.argv[1:]))
    print(request("POST", url, data=data).json())

import mrequests


def request(method, url, data=None, json=None, headers=None, encoding=None):
    if isinstance(data, dict):
        from urlencode import urlencode

        data = urlencode(data, encoding=encoding)
        headers = {} if headers is None else headers
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    return mrequests.request(method, url, data=data, json=json, headers=headers)


if __name__ == "__main__":
    import sys

    host = "http://httpbin.org/"
    url = host + "post"
    data = dict((arg.split("=") for arg in sys.argv[1:]))
    r = request("POST", url, data=data)

    if r.status_code == 200:
        print(r.json())
    else:
        print("Request failed. Status: {}".format(r.status_code))

    r.close()

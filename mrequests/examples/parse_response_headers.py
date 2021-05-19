import mrequests


class MyResponse(mrequests.Response):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.headers = {}

    def add_header(self, data):
        # let base class handle headers, which influence response parsing
        self._parse_header(data)
        name, value = data.decode('utf-8').rstrip('\r\n').split(':', 1)
        self.headers[name.lower()] = value.strip()


def request(*args, **kw):
    kw.setdefault('response_class', MyResponse)
    return mrequests.request(*args, **kw)

host = "http://httpbin.org/"
#host = "http://localhost/"
url = host + "get"
r = request("GET", url)

if r.status_code == 200:
    print("Response headers:")
    print("=================\n")

    for name, value in r.headers.items():
        print("{}: {}".format(name, value))

    print()
    print("Response body:")
    print("==============\n")
    print(r.json())
else:
    print("Request failed. Status: {}".format(resp.status_code))

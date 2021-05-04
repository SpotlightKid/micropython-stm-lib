import mrequests
from urlencode import urlencode

DOH_IP = "1.1.1.1"
DOH_SERVER = b"cloudflare-dns.com"
DOH_PATH = "/dns-query"


def gethostbyname(name):
    params = urlencode({
        "name": name,
        "type": "A"
    })
    headers = {
        b"accept": b"application/dns-json",
        b"user-agent": b"mrequests.py",
        b"Host": DOH_SERVER
    }
    req = mrequests.get(
        "https://{}{}?{}".format(DOH_IP, DOH_PATH, params),
        headers=headers
    )
# ~    print(req.status_code)
    if req.status == 200:
        reply = req.json()
    else:
        reply = {}

    req.close()

    if reply.get("Status") == 0:
        return [item["data"] for item in reply.get("Answer", [])]


if __name__ == '__main__':
    import sys
    #name = sys.argv[1]
    name = "httpbin.org"
    res = gethostbyname(name)
    if res:
        print(" ".join(res))
    else:
        print("Could not resolve host name '{}'.".format(name), file=sys.stderr)

import zlib
import mrequests as requests


host = "http://httpbin.org/"
#host = "http://localhost/"
url = host + "deflate"
r = requests.get(url, headers={"TE": "deflate"})

if r.status_code == 200:
    print("Response body length: %i" % len(r.content))
    text = zlib.decompress(r.content).decode("utf-8")
    print("Deflated response text length: %i" % len(text))
    print("Response text:\n")
    print(text)
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()

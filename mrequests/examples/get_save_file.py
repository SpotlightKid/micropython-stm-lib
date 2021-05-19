import mrequests

host = 'http://httpbin.org/'
#host = "http://localhost/"
url = host + "image"
filename = "image.png"
r = mrequests.get(url, headers={b"accept": b"image/png"})

if r.status_code == 200:
    r.save(filename)
    print("Image saved to '{}'.".format(filename))
else:
    print("Request failed. Status: {}".format(r.status_code))

r.close()

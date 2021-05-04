import mrequests as requests


host = 'http://httpbin.org/'
url = host + "get"
r = requests.get(url, headers={"Accept": "application/json"})
print(r)
print(r.content)
print(r.text)
print(r.json())
r.close()

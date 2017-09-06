from http.client import HTTPConnection

c = HTTPConnection('localhost', 8080)
c.request('POST', '/process', '{"yolo": 1}')
doc = c.getresponse().read().decode()
print(doc)

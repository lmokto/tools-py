import Queue
import threading
import urllib2
# http://stackoverflow.com/questions/2846653/python-multithreading-for-dummies
# called by each thread


def get_url(q, url):
	
	proxy = urllib2.ProxyHandler({'http': 'http://##@#:##@##:##'})
	auth = urllib2.HTTPBasicAuthHandler()
	opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
	urllib2.install_opener(opener)
	q.put(urllib2.urlopen(url).read())

theurls = ["http://52.10.233.24/v1/circuits/9031/latest", "http://52.10.233.24/v1/circuits/9033/latest"]

q = Queue.Queue()

for u in theurls:
    t = threading.Thread(target=get_url, args = (q,u))
    t.daemon = True
    t.start()

s = q.get()
print s
# coding=utf8
import sys
import urllib2
import os
import re
import cPickle
import time
import Queue

class ProgressPrinter(object):
    """simple logger"""
    def __init__(self, interval = 1000, prefix = '', target = 0):
        super(ProgressPrinter, self).__init__()
        self.prefix = prefix
        self.interval = interval
        self.counter = 0
        self.target = target

    def start(self, target = 0, interval = 0):
        self.counter = 0
        if target != 0: self.target = target
        if interval != 0: self.interval = interval
    def finish(self):
        sys.stderr.write(' done.\n')
        self.counter = 0
    def tick(self):
        self.counter += 1
        if self.counter % self.interval == 0:
            if self.target != 0:
                sys.stderr.write('\r' + str(self.prefix) + ' %d/%d ...'%(self.counter, self.target))
            else:
                sys.stderr.write('\r' + str(self.prefix) + ' %d ...'%self.counter)
    def set_interval(self, interval):
        self.interval = int(interval)


class CacheManager(object):
    """simple cache manager."""
    def __init__(self, path='./.tmp'):
        super(CacheManager, self).__init__()
        self.root_dir = path
        if not os.path.exists(path):
            os.makedirs(path)

    def get(self, name, datatype='pickle'):
        path = os.path.join(self.root_dir, name)
        if os.path.exists(path):
            try:
                if datatype == 'pickle':
                    o = cPickle.load(open(path))
                elif datatype == 'text':
                    o = open(path).read()
                return o
            except:
                sys.stderr.write('[CACHE] load error: %s\n' % path)
                return None
        else:
            sys.stderr.write('[CACHE] cache miss: %s\n' % name)
            return None

    def save(self, name, o, datatype='pickle'):
        path = os.path.join(self.root_dir, name)
        try:
            if datatype == 'pickle':
                o = cPickle.dump(o, open(path, 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)
            elif datatype == 'text':
                open(path, 'w').write(o.encode('utf8'))
            elif datatype == 'raw':
                open(path, 'wb').write(o)
        except Exception, e:
            print e
            sys.stderr.write('[CACHE] save error: %s\n' % path)

    def purge(self, name):
        path = os.path.join(self.root_dir, name)
        if not os.path.exists(path):
            return
        try:
            os.remove(path)
        except:
            sys.stderr.write('[CACHE] purge error: %s\n' % path)

def urlget_h(url):
	retry=3
	s=''
	while retry > 0:
		try:
			request = urllib2.Request(url)
			request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36')
			# request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
			# request.add_header('Accept-Encoding', 'deflate, sdch')
			# request.add_header('Cookie', '')
			s=urllib2.urlopen(request, timeout=10).read()
			break
		except Exception as e:
			retry -= 1
			time.sleep(1)
	if s:
		return s
	else:
		print 'url connect failed'
		return ''


def urlget(url):
    retry = 3
    s = ''
    while retry > 0:
        try:
            s = urllib2.urlopen(url).read()
            if s:
                break
        except:
            print 'retry', url
            time.sleep(1)
            retry -= 1
	if s:
		return s
	else:
		print 'url connect failed'
		return ''

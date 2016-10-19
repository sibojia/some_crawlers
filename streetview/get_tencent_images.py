# coding=utf8
import urllib2, os, sys
import json, time, Queue
from xml.dom.minidom import parse, parseString

def urlget(url):
	try:
		return urllib2.urlopen(url, timeout=5).read()
	except:
		print "urlopen wait 1 sec"
		time.sleep(1)
		try:
			return urllib2.urlopen(url, timeout=5).read()
		except:
			return ''

# Pattern: x:horizontal y:vertical level:low/high
# level 0: x:[0,8) y:[0,4)
# level 1: x:[0,16) y:[0,8)
def trydown():
	for x in range(8,16):
		for y in range(8):
			for level in [1]:
				s=urlget("http://sv3.map.qq.com/tile?svid=10011039140321104652200&x=%d&y=%d&from=web&level=%d"%(x,y,level))
				open('tmp/%d_%d_%d.jpg'%(x,y,level),'w').write(s)
				print x,y,level

trydown()

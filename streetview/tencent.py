# coding=utf8
import urllib2, os, sys
import json, time, Queue
from xml.dom.minidom import parse, parseString

OUTDIR = 'tencent_xml'
os.system('mkdir -p %s'%OUTDIR)

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

def get_xml(svid):
	xmlstr = urlget(u'http://sv.map.qq.com/sv?pf=web&svid=%s&from=http://map.qq.com/'%svid)
	xmlstr = xmlstr.replace("&", "and")
	return xmlstr

# For trying ids in error.log
#for line in open('error.log').readlines():
	#xmlstr = get_xml(line.strip())
	#if xmlstr:
		#open(os.path.join(OUTDIR, line.strip()+'.xml'), 'w').write(xmlstr)
		#print line,
#sys.exit()

dupset = set()
for i in os.listdir(OUTDIR):
	dupset.add(unicode(i.split('.')[0]))
q = Queue.deque()
qset = set()

if os.path.exists('svid_queue.txt'):
	lines = open('svid_queue.txt').readlines()
	for l in lines:
		q.append(unicode(l.strip()))
		qset.add(unicode(l.strip()))
else:
	q.append(u'10011021130417114051700')
	qset.add(u'10011021130417114051700')

# For debug
#lines = open('error.log').readlines()
#for l in lines:
	#q.appendleft(unicode(l.strip()))
	#qset.add(unicode(l.strip()))
	#dupset.remove(unicode(l.strip()))

count = 0
print "Start with %d items in queue" % len(q)
while q.count > 0:
	curid = q.popleft()
	qset.remove(curid)
	if curid in dupset:
		continue
	xmlstr = get_xml(curid)
	if len(xmlstr) > 0:
		count += 1
		if count % 100 == 0:
			print "Processed %d. Current: %s" % (count, curid)
			open('svid_queue.txt','w').write('\n'.join(q))
		open(os.path.join(OUTDIR, curid+'.xml'), 'w').write(xmlstr)
		dupset.add(curid)
		try:
			xmldom = parseString(xmlstr).documentElement
			scenes = xmldom.getElementsByTagName('all_scenes')[0].getElementsByTagName('all_scene')
			for scene in scenes:
				svid = scene.getAttribute('svid')
				if svid not in qset:
					qset.add(svid)
					q.append(svid)
		except:
			print "Error parsing %s" % curid
			open("error.log","a").write(curid+'\n')
	else:
		print "Error fetching %s" % curid
		open("error.log","a").write(curid+'\n')

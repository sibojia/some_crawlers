# coding: utf-8
import requests
import json, sys
import re

fin=sys.argv[1]
fout=sys.argv[2]

data={}
j=json.load(open(fin))
print 'Loaded %d items' % len(j)
for item in j:
	s=requests.get('http://www.ibilibili.com/video/av%s' % item['aid'])
	ro= re.compile(r'<em.*?title="(.*?)".*?"([^"]*?bilibilijj.*?)".*?视频',re.DOTALL)
	matches=ro.findall(s.content)
	if len(matches) == 1:
		data[matches[0][1]] = matches[0][0]
	elif len(matches) > 1:
		print 'Encountered video with %d episodes: %s' % (len(matches), item['title'])
		for m in matches:
			title='%s-%s'%(item['title'].encode('utf8'), m[0])
			if data.has_key(m[1]):
				print "Skip duplicate video: %s" % title
			else:
				data[m[1]] = title
	else:
		print 'Parse video failed for %s, link: http://www.ibilibili.com/video/av%s'%(item['title'], item['aid'])
print 'Added %d links' % len(data)
datalist = [[data[d], d] for d in data]
for t in datalist:
	t[0] = re.sub(r'[\\/:\*\?"<>\|]','_', t[0])
	t[0] = t[0]+'.mp4'
datalist.sort()
with open(fout,'w') as f:
	for d in datalist:
		f.write('%s\n%s\n'%(d[0],d[1]))

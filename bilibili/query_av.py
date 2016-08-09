# coding: utf-8
import requests
import json, sys

# currently only support all video for a person ID
mid=sys.argv[1]
fout=sys.argv[2]
s=requests.get('http://space.bilibili.com/ajax/member/getSubmitVideos?mid=%s&pagesize=300&tid=0&keyword=&page=1' % mid)
j=json.loads(s.content)
jd=j['data']
titles=[{'aid':x['aid'], 'title':x['title']} for x in jd['vlist']]
open(fout,'w').write(json.dumps(titles,indent=0,ensure_ascii=False).encode('utf8'))


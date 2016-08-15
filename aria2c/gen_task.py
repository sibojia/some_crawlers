import sys, os

fin=sys.argv[1]
fout=sys.argv[2]
rootdir=sys.argv[3]

open(fout+'.conf','w').write('''continue
dir=%s
input-file=%s
max-connection-per-server=1
max-concurrent-downloads=1''' % (os.path.abspath(rootdir), fout+'.input'))

vlist=open(fin).read().splitlines()
data=[]
for i in xrange(len(vlist)/2):
	data.append([vlist[i*2], vlist[i*2+1]])
with open(fout+'.input','w') as f:
	for d in data:
		f.write('%s\n  out=%s\n' % (d[1], d[0]))

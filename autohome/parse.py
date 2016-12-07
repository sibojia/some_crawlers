import os, sys, cPickle

data = cPickle.load(open('result.pkl'))
ftype = open('series.txt', 'w')
ffiles = open('images.txt', 'w')

bid = 0
for brand in data:
    bname = brand['name'].decode('gbk').encode('utf8')
    fid = 0
    for fct in brand['factories']:
        fcname = fct['name'].decode('gbk').encode('utf8')
        sid = 0
        for serie in fct['series']:
            pid = 0
            sname = serie['name'].decode('gbk').encode('utf8')
            path = '%03d/%02d/%02d' % (bid, fid, sid)
            ftype.write('%s,%s,%s,%s\n' % (path, bname, fcname, sname))
            for purl in serie['pic_url']:
                path = 'images/%03d/%02d/%02d/%04d.jpg' % (bid, fid, sid, pid)
                pname = purl['name'].decode('gbk').encode('utf8')
                color = purl['color'].encode('utf8')
                ffiles.write('%s,%s,%s,%s,%s,%s\n' % (path, bname, fcname, sname, pname, color))
                pid += 1
            sid += 1
        fid += 1
    bid += 1

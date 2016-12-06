# coding=utf8
import sys
sys.path.append('..')
from common import *
from easydict import EasyDict as edict
import copy

cm = CacheManager()
SERIE_NAME = 'autohome_series'
SURL_NAME = 'autohome_serie_urls'
PURL_NAME = 'autohome_pic_urls'
host = 'http://car.autohome.com.cn'

def get_series():
    # cm.purge(SERIE_NAME)
    cache = cm.get(SERIE_NAME)
    if cache:
        return cache
    allstr = urllib2.urlopen('http://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=2').read()
    # print allstr
    cm.save('html', allstr, 'text')
    brands = re.findall(r"<h3><a href='(.*?)'><i class=.*?></i>(.*?)<em>\((.*?)\)</em></a></h3>", allstr)
    print "num brands:", len(brands)
    i = 0
    jdata = []
    for b in brands:
        print i, b[0]
        i += 1
        bid = re.findall(r"pic/brand-(.*?)\.html", b[0])[0]
        bname = b[1]
        bnum = int(b[2])
        jbrand = {"id": bid, "name": bname, "num": bnum, "factories": []}
        brandstr = urlget('http://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=2&brandId=%s' % bid)
        if brandstr:
            curfind = re.findall('<dl>(.*?)</dl>', brandstr)
            if len(curfind) > 0:
                curbrandstr = curfind[0]
            else:
                curbrandstr = re.findall('<dl>(.*)', brandstr)[0]
            fcts = re.findall(r"<dt><a id='fct_(.*?)'.*?</i>(.*?)</a></dt>", curbrandstr)
            dt_occurance = [m.start() for m in re.finditer('<dt>', curbrandstr)]
            snum_count = 0
            for _i in range(len(dt_occurance)):
                fname = fcts[_i][1].strip()
                fctid = fcts[_i][0]
                jfct = {"id": fctid, "name": fname, "series":[]}
                if _i + 1 == len(dt_occurance):
                    curfctstr = curbrandstr[dt_occurance[_i]:]
                else:
                    curfctstr = curbrandstr[dt_occurance[_i]: dt_occurance[_i+1]]
                series = re.findall(r"<dd><a id='series_(.*?)' href='(.*?)'>(.*?)<em>(.*?)\(([^\(]*?)\)</em></a></dd>", curfctstr)
                for s in series:
                    sid = s[0]
                    surl = s[1]
                    sname = s[2]
                    sext = s[3]
                    snum = int(s[4])
                    jfct["series"].append({"id": sid, "url": surl, "name": sname, "extra": sext, "num": snum})
                    snum_count += snum
                jbrand["factories"].append(jfct)
            if bnum != snum_count:
                print bnum, snum_count
        jdata.append(jbrand)
        # time.sleep(0.1)
    cm.save(SERIE_NAME, jdata)
    return jdata

def get_pic_url(sdata):
    urldata = cm.get(SURL_NAME)
    if urldata is None:
        urldata = copy.deepcopy(sdata)
    for brand in urldata:
        print '', brand['name'].decode('gbk')
        bnum = 0
        for fct in brand['factories']:
            print ' ', fct['name'].decode('gbk')
            fnum = 0
            for serie in fct['series']:
                print '  ', serie['name'].decode('gbk')
                urllist = ['/pic/series/%s-1.html' % serie['id']]
                ind = 0
                snum = 0
                if serie.has_key('pics') and len(serie['pics']) == serie['num']:
                    # SKIP
                    snum = serie['num']
                else:
                    serie['pics'] = []
                    while ind < len(urllist):
                        pstr = urlget_h(host + urllist[ind])
                        if ind == 0:
                            pages = re.findall('a href="(/pic/series/146-1-.*?\.html)', pstr)
                            if len(pages): urllist.extend(pages)
                        pics = re.findall('<li><a href="(/photo/series/.*?\.html)" title="(.*?)"', pstr)
                        serie['pics'].extend(pics)
                        snum += len(pics)
                        ind += 1
                serie['num'] = snum
                fnum += snum
            fct['num'] = fnum
            bnum += fnum
        brand['num'] = bnum
        cm.save(SURL_NAME, urldata)
    print 'Done.'

def get_dl_url():
    pp = ProgressPrinter(interval=10)
    sdata = cm.get(PURL_NAME)
    if sdata is None:
        sdata = cm.get(SURL_NAME)
    num = 0
    for brand in sdata:
        print '', brand['name'].decode('gbk')
        for fct in brand['factories']:
            # print ' ', fct['name'].decode('gbk')
            for serie in fct['series']:
                if serie.has_key('pic_url') and len(serie['pic_url']) == len(serie['pics']):
                    continue
                serie['pic_url'] = []
                for url, mname in serie['pics']:
                    pp.tick()
                    pstr = urlget_h(host + url.replace('photo', 'bigphoto'))
                    match_p = re.findall('id="img" src="(.*?)"', pstr)
                    if len(match_p) != 1:
                        print "Error!", url, mname
                        continue
                    else:
                        purl = match_p[0]
                    match_c = re.findall(u'外观颜色.*?class="red".*?>(.*?)<span>', pstr.decode('gbk'))
                    if len(match_c) == 1:
                        color = match_c[0]
                    else:
                        color = ''
                    serie['pic_url'].append({'name': mname, 'url': purl, 'color': color})
                    num += 1
        cm.save(PURL_NAME, sdata)
        time.sleep(1)
    print num

dpp = ProgressPrinter(interval=1)
class DownQueue(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue=queue
    def run(self):
        while not self.queue.empty():
            item = self.queue.get()
            dpath = os.path.split(item[0])[0]
            if os.path.exists(item[0]):
                dpp.tick()
                continue
            if not os.path.exists(dpath):
                os.makedirs(dpath)
            img = urlget_h(item[1])
            if img is not None:
                open(item[0], 'wb').write(img)
                dpp.tick()
            else:
                writeLock.acquire()
                open('error_img.log', 'a').write(item[0]+' '+item[1]+'\n')
                writeLock.release()

def download_imgs():
    sdata = cm.get(PURL_NAME)
    pdata = queue.Queue()
    length = 0
    bid = 0
    for brand in sdata:
        fid = 0
        for fct in brand['factories']:
            sid = 0
            for serie in fct['series']:
                pid = 0
                for purl in serie['pic_url']:
                    path = 'images/%03d/%02d/%02d/%04d.jpg' % (bid, fid, sid, pid)
                    purl['file_path'] = path
                    pdata.put((path, host + purl['url']))
                    length += 1
                    pid += 1
                sid += 1
            fid += 1
        bid += 1
    cm.save(PURL_NAME, sdata)
    print "Start task with %d ids"%length
    threads = []
    for i in range(8):
        t = DownQueue(queue)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def main():
    # sdata = get_series()
    # urls = get_pic_url(sdata)
    get_dl_url()
    download_imgs()

if __name__ == '__main__':
    main()

# coding=utf8
import sys
sys.path.append('..')
from common import *
from easydict import EasyDict as edict
import copy

cm = CacheManager()
SERIE_NAME = 'autohome_series'
SURL_NAME = 'autohome_serie_urls'

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
    host = 'http://car.autohome.com.cn'
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
    sdata = cm.get(SURL_NAME)
    num = 0
    for brand in sdata:
        # print '', brand['name'].decode('gbk')
        for fct in brand['factories']:
            # print ' ', fct['name'].decode('gbk')
            for serie in fct['series']:
                pass
    print num


def main():
    # sdata = get_series()
    # urls = get_pic_url(sdata)
    get_dl_url()

if __name__ == '__main__':
    main()

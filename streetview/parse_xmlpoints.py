# coding=utf8
import urllib2, os, sys
import json, time, Queue
from xml.dom.minidom import parse, parseString
import cPickle
sys.path.append('..')
from common import *
import cv2
import numpy as np

def read_pos(xmlstr):
    xmldom = parseString(xmlstr).documentElement
    lng=xmldom.getElementsByTagName('addr')[0].getAttribute('x_lng')
    lat=xmldom.getElementsByTagName('addr')[0].getAttribute('y_lat')
    return (float(lng), float(lat))

def read_all_files(root, interval=20):
    l=os.listdir(root)
    data=[]
    counter = ProgressPrinter(target=len(l)/interval)
    counter.start()
    skip=0
    for fname in l:
        skip+=1
        if skip==interval:
            skip=0
        else:
            continue
        xmlstr=open(os.path.join(root, fname)).read()
        try:
            pos=read_pos(xmlstr)
            data.append((pos, fname.split('.')[0]))
        except Exception as e:
            print "error", fname
            pass
        counter.tick()
    counter.finish()
    return data

def get_point_image(points, width=800, height=600):
    minbound=[180,90]
    maxbound=[-180,-90]
    for p in points:
        if p[0][0] > maxbound[0]: maxbound[0]=p[0][0]
        if p[0][1] > maxbound[1]: maxbound[1]=p[0][1]
        if p[0][0] < minbound[0]: minbound[0]=p[0][0]
        if p[0][1] < minbound[1]: minbound[1]=p[0][1]
    minbound[0]-=0.1*(maxbound[0]-minbound[0])
    minbound[1]-=0.1*(maxbound[1]-minbound[1])
    maxbound[0]+=0.1*(maxbound[0]-minbound[0])
    maxbound[1]+=0.1*(maxbound[1]-minbound[1])
    x_delta=maxbound[0]-minbound[0]
    y_delta=maxbound[1]-minbound[1]
    img=np.ones((height, width,3), dtype=np.ubyte)*80
    for p in points:
        x=(p[0][0]-minbound[0])*width/x_delta
        y=height-(p[0][1]-minbound[1])*height/y_delta
        img[y,x]=(255,150,150)
    def f_get_pos(ix, iy):
        return (ix*x_delta/width+minbound[0], (height-iy)*y_delta/height+minbound[1])
    return img, f_get_pos

def on_mouse(event,x,y,flags,f_get_pos):
    if event==cv2.EVENT_LBUTTONDBLCLK:
        gx,gy=f_get_pos(x,y)
        print "(%d, %d) -> (%f, %f)" % (x,y,gx,gy)

def main():
    if False:
        points=read_all_files('./tencent_xml', interval=1)
        cPickle.dump(points, open('pdata-tmp.pkl','wb'), cPickle.HIGHEST_PROTOCOL)
    else:
        points=cPickle.load(open(sys.argv[1]))
    img,f_get_pos=get_point_image(points, width=1024, height=1024)
    cv2.imwrite("pmap.png", img)
    cv2.imshow("map",img)
    cv2.setMouseCallback('map',on_mouse,f_get_pos)
    cv2.waitKey(0)

if __name__ == "__main__":
    main()

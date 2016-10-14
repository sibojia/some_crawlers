# coding=utf8
import urllib2, os, sys
import json, time, Queue
from xml.dom.minidom import parse, parseString

xmlstr=open(sys.argv[1]).read()
xmldom = parseString(xmlstr).documentElement
lng=xmldom.getElementsByTagName('addr')[0].getAttribute('x_lng')
lat=xmldom.getElementsByTagName('addr')[0].getAttribute('y_lat')
print lng, lat
#scenes = xmldom.getElementsByTagName('all_scenes')[0].getElementsByTagName('all_scene')

# coding=utf8
import urllib2, os, sys
import json, time, cPickle
from xml.dom.minidom import parse, parseString
import cv2
import numpy as np
import threading, Queue

sys.path.append('..')
from common import *

# Pattern: x:horizontal y:vertical level:low/high
# level 0: x:[0,8) y:[0,4)
# level 1: x:[0,16) y:[0,8)

writeLock=threading.Lock()
counter=ProgressPrinter(interval=1)
counter.start()

class DownQueue(threading.Thread):
	def __init__(self,queue):
		threading.Thread.__init__(self)
		self.queue=queue
	def run(self):
		while not self.queue.empty():
			svid=self.queue.get()
			fname='tencent_images/%s.jpg'%svid
			if os.path.exists(fname):
				continue
			img=get_surround_image(svid, 1)
			if img is not None:
				cv2.imwrite(fname,img)
				counter.tick()
			else:
				writeLock.acquire()
				open('error_img.log', 'a').write(svid+'\n')
				writeLock.release()

def urlget(url):
	retry=3
	s=''
	while retry > 0:
		try:
			request = urllib2.Request(url)
			request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36')
			request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
			request.add_header('Accept-Encoding', 'gzip, deflate, sdch')
			request.add_header('Cookie', 'new_uvid=2849557747581161062; pac_uid=1_373135034; o_cookie=373135034; pgv_pvi=5973000192; pgv_pvid=9970365696; mpuv=Cq0EVVfskusGkiv4NehYAg==; ptui_loginuin=373135034; pt2gguin=o0373135034; RK=5fl7SH/2Pp; ptcz=02d1997a84fd941356fe7f3619881dd341e6288437cb634c9301a7d686e6ea44; pgv_si=s400505856; webwx_data_ticket=gSfEnVcL6YCii+iagImOsnYl')
			s=urllib2.urlopen(request, timeout=10).read()
			break
		except Exception as e:
			retry -= 1
			time.sleep(1)
	if s:
		return s
	else:
		print 'url connect failed'
		return ''

# coding=utf8
import cv2, os, sys
import numpy as np

def concat_images(images, rows, cols):
	assert(rows*cols==len(images))
	h=images[0].shape[0]
	w=images[0].shape[1]
	cimage=np.zeros((h*rows, w*cols, 3), dtype=np.ubyte)
	for r in range(rows):
		for c in range(cols):
			cimage[r*h:(r+1)*h, c*w:(c+1)*w]=images[r*cols+c]
	return cimage

def trydown():
	for x in range(8,16):
		for y in range(8):
			for level in [1]:
				s=urlget("http://sv3.map.qq.com/tile?svid=10011039140321104652200&x=%d&y=%d&from=web&level=%d"%(x,y,level))
				open('tmp/%d_%d_%d.jpg'%(x,y,level),'w').write(s)
				print x,y,level

def tryconcat():
	flist=[]
	for j in range(8):
		for i in range(16):
			flist.append(cv2.imread('tmp/%d_%d_%d.jpg'%(i,j,1)))
	img=concat_images(flist, 8, 16)
	cv2.imwrite("temp_hd.jpg", img)

def get_surround_image(svid, level):
	if level == 0:
		xmax=8
		ymax=4
	else:
		xmax=16
		ymax=8
	images=[]
	for y in range(ymax):
		for x in range(xmax):
			s=urlget("http://sv3.map.qq.com/tile?svid=%s&x=%d&y=%d&from=web&level=%d"%(svid,x,y,level))
			if not s:
				return None
			arr=np.asarray(bytearray(s), dtype=np.uint8)
			img=cv2.imdecode(arr, cv2.cv.CV_LOAD_IMAGE_COLOR)
			if img is None:
				return None
			images.append(img)
	sur_image=concat_images(images, ymax, xmax)
	return sur_image

def add_task_by_gps_range(data, xr, yr):
	queue=Queue.Queue()
	length=0
	for d in data:
		x=d[0][0]
		y=d[0][1]
		if x<xr[1] and x>xr[0] and y<yr[1] and y>yr[0]:
			queue.put(d[1])
			length+=1
	return queue,length

if __name__ == "__main__":
	data=cPickle.load(open('pdata-1017.pkl'))
	queue,length=add_task_by_gps_range(data, [116.314146, 116.338340], [39.987957, 40.000994])
	print "Start task with %d ids..."%length
	threads=[]
	for i in range(4):
		t=DownQueue(queue)
		t.start()
		threads.append(t)
	for t in threads:
		t.join()

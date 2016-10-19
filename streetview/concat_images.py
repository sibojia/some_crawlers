# coding=utf8
import cv2, os, sys
import numpy as np

def concat_images(imagelist, rows, cols):
	assert(rows*cols==len(imagelist))
	images=[cv2.imread(i) for i in imagelist]
	h=images[0].shape[0]
	w=images[0].shape[1]
	cimage=np.zeros((h*rows, w*cols, 3), dtype=np.ubyte)
	for r in range(rows):
		for c in range(cols):
			cimage[r*h:(r+1)*h, c*w:(c+1)*w]=images[r*cols+c]
	return cimage


def tryconcat():
	flist=[]
	for j in range(8):
		for i in range(16):
			flist.append('tmp/%d_%d_%d.jpg'%(i,j,1))
	img=concat_images(flist, 8, 16)
	cv2.imwrite("temp_hd.jpg", img)

tryconcat()

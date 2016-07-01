import json,os,sys,cv2
from util import *

def color_hash(i):
	return ((i*50)%205 + 50, (i*70)%205 + 50, (i*90)%205 + 50)

def show(labelpath, imgroot, rects):
	fmap=open(labelpath+'/GuidMapping.txt').readlines()
	i=0
	while i < len(rects):
		tok=fmap[i].strip().split('"')
		imgpath=tok[0].replace('\\','/')
		img=cv2.imread(imgroot+'/'+imgpath)
		for rect in rects[i]:
			if len(rect) >= 5:
				color = color_hash(rect[4])
			else:
				color = (100,255,100)
			cv2.rectangle(img, (int(rect[0]), int(rect[1])), (int(rect[0]+rect[2]), int(rect[1]+rect[3])), color, 2)
		print imgpath
		cv2.imshow("a", img)
		key = cv2.waitKey(0)
		if key & 0xFF == 27:
			break
		if key & 0xFF == 82:
			i -= 1
			if i < 0: i = 0
		else:
			i += 1

if __name__ == '__main__':
	labelpath=sys.argv[1]
	imgroot=sys.argv[2]
	rawoutputpath=sys.argv[3]
	rects = read_raw_rects(rawoutputpath)
	show(labelpath, imgroot, rects)

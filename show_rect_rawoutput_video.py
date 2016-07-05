import json,os,sys,cv2
from util import *

def color_hash(i):
	i += 1
	return ((i*50)%205 + 50, (i*80)%205 + 50, (i*100)%205 + 50)

def show(videopath, rects):
	cap=cv2.VideoCapture(videopath)
	if not cap.isOpened():
		print "Video open failed"
		return
	i=0
	while i < len(rects):
		_, img=cap.read()
		for rect in rects[i]:
			if len(rect) >= 5:
				color = color_hash(rect[4])
			else:
				color = (100,255,100)
			cv2.rectangle(img, (int(rect[0]), int(rect[1])), (int(rect[0]+rect[2]), int(rect[1]+rect[3])), color, 2)
		cv2.imshow("a", img)
		key = cv2.waitKey(0)
		if key & 0xFF == 27:
			break
		i += 1

if __name__ == '__main__':
	videopath=sys.argv[1]
	rawoutputpath=sys.argv[2]
	rects = read_raw_rects(rawoutputpath)
	show(videopath, rects)

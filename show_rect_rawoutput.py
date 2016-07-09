# coding=utf8
import json,os,sys,cv2
from util import *
import Image, ImageDraw, ImageFont
import numpy as np

def color_hash(i):
	i += 1
	return (int((i*50)%205 + 50), int((i*80)%205 + 50), int((i*100)%205 + 50))

USE_PIL=True
VIDEO_OUT=False

def show(labelpath, imgroot, rects, attr = None):
	if VIDEO_OUT:
		v = cv2.VideoWriter()
		v.open("temp_out.avi", cv2.cv.CV_FOURCC('X', 'V', 'I', 'D'), 30, (1920,1080), True)
	fmap=open(labelpath+'/GuidMapping.txt').readlines()
	font = ImageFont.truetype("wqy-microhei.ttc",22)
	i=0
	img=np.zeros((1080,1920,3), dtype=np.uint8)
	while i < len(rects):
		tok=fmap[i].strip().split('"')
		imgpath=tok[0].replace('\\','/')
		img=cv2.imread(imgroot+'/'+imgpath)

		# convert to PIL image (color BGR)
		if USE_PIL:
			pil_im = Image.fromarray(img)
			draw = ImageDraw.Draw(pil_im)

		for rect in rects[i]:
			if len(rect) >= 5:
				color = color_hash(rect[4])
				if USE_PIL:
					if attr and attr.has_key(rect[4]):
						att = attr[rect[4]]
						if (int(att[0]) == -1 or i>=int(att[0])) and (int(att[1]) == -1 or i<=int(att[1])):
							s = "#" + str(int(rect[4])) + " " + " ".join(att[2:])
							s = " ".join(att[2:])
							draw.text((int(rect[0] + 2), int(rect[1]) -24), unicode(s,"utf-8"), font=font, fill=(50,50,50))
							draw.text((int(rect[0]), int(rect[1]) - 26), unicode(s,"utf-8"), font=font, fill=(255,222,0))
					else:
						pass
						# draw.text((int(rect[0]), int(rect[1]) - 26), unicode(str(rect[4]),"utf-8"), font=font, fill=(255,222,0))
				else:
					cv2.putText(img, str(int(rect[4])), (int(rect[0]), int(rect[1]) - 5), cv2.FONT_HERSHEY_DUPLEX, 0.8, color)
			else:
				color = (100,255,100)
			if USE_PIL:
				pass
				color = (0,222,255)
				draw.rectangle([int(rect[0]), int(rect[1]), int(rect[0]+rect[2]), int(rect[1]+rect[3])], outline=color[::-1])
				draw.rectangle([int(rect[0]+1), int(rect[1]+1), int(rect[0]+rect[2]+1), int(rect[1]+rect[3]+1)], outline=color[::-1])
			else:
				cv2.rectangle(img, (int(rect[0]), int(rect[1])), (int(rect[0]+rect[2]), int(rect[1]+rect[3])), color, 2)
		print imgpath
		# cv2.imwrite("temp_output/%s"%imgpath, img)
		if USE_PIL:
			img = np.array(pil_im)
		if VIDEO_OUT:
			key = 1
			v.write(img)
		else:
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
	attr=None
	if len(sys.argv) == 5:
		attr = read_attr(sys.argv[4])
	rects = read_raw_rects(rawoutputpath)
	show(labelpath, imgroot, rects, attr)

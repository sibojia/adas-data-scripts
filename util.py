import cv2

def read_raw_rects(f):
	rects = []
	lines = open(f).readlines()
	for l in lines:
		tok = l.strip().split(' ')
		if len(tok) == 1:
			rects.append([])
		else:
			rects[-1].append([float(i) for i in tok])
	return rects

def dump_raw_rects(fout, rects2d, includeid = False):
	f = open(fout, 'w')
	for r in rects2d:
		f.write("%d\n" % len(r))
		for rr in r:
			if includeid:
				f.write(' '.join([str(int(j)) for j in rr]) + '\n')
			else:
				f.write(' '.join([str(int(j)) for j in rr[:-1]]) + '\n')
	f.close()

def read_all_images(labelpath, imgroot):
	fmap=open(labelpath+'/GuidMapping.txt').readlines()
	imgs = []
	i=0
	for item in fmap:
		tok=item.strip().split('"')
		imgpath=tok[0].replace('\\','/')
		img=cv2.imread(imgroot+'/'+imgpath)
		imgs.append(img)
		i+=1
		# if i>100:break
	return imgs

# def merge_rects(rects2d1, rects2d2):
# 	def getstat(rect2d):
# 		return len(rect2d), max(max([i[4] for ])

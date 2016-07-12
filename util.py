import cv2

def read_raw_rects(f):
	''' Return: array of each frame: [[l, t, w, h_of_rect1], ...]'''
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

def read_lanes(s):
	''' Return: array of each frame: [[x_cord_of_line1, y_cord_of_line1], ...]'''
	fin=open(s).readlines()
	data = []
	for line in fin:
	    tok=line.strip().split(' ')
	    if len(tok) == 1:
	        lanenum = int(tok[0])
	        if lanenum == 0:
				data.append([])
	        points=[]
	    else:
	        lanenum -= 1
	        xs=[float(i) for i in tok[0::2]]
	        ys=[float(i) for i in tok[1::2]]
	        points.append([xs,ys])
	        if lanenum == 0:
	            data.append(points)
	return data

def dump_lanes(fout, lines2d):
	f=open(fout, 'w')
	for lines in lines2d:
		f.write("%d\n" % len(lines))
		for line in lines:
			if len(line[0]) == 0:
				print lines
			f.write(' '.join([str(i) for j in zip(line[0], line[1]) for i in j]) + '\n')
	f.close()

def read_all_images(labelpath, imgroot):
	''' Return: array of opencv mat'''
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

def read_attr(fin):
	''' Return: directory of trackid => [starti, endi, attr...]'''
	lines = open(fin).readlines()
	h={}
	for i in lines:
		tok=i.strip().split(' ')
		h[int(tok[0])] = tok[1:]
	return h

# def merge_rects(rects2d1, rects2d2):
# 	def getstat(rect2d):
# 		return len(rect2d), max(max([i[4] for ])

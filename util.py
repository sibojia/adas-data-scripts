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

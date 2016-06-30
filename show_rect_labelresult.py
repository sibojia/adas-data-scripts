import json,os,sys,cv2
labelpath=sys.argv[1]
imgroot=sys.argv[2]
fmap=open(labelpath+'/GuidMapping.txt').readlines()
for item in fmap:
	tok=item.strip().split('"')
	imgpath=tok[0].replace('\\','/')
	fj=open(labelpath+'/Label/'+tok[1]+'.info').read()
	js=json.loads(fj)
	# img=cv2.imread('/home/user/1.jpg')
	img=cv2.imread(imgroot+'/'+imgpath)
	if js.has_key('Rects'):
		for rect in js['Rects']:
			cv2.rectangle(img, (int(rect['x']), int(rect['y'])), (int(rect['x']+rect['width']), int(rect['y']+rect['height'])), (0,255,0),2)
	cv2.imshow("a", img)
	key = cv2.waitKey(0)
	if key & 0xFF == 27:
		break
	print imgpath

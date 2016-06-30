import cv2
import os,sys

cap=cv2.VideoCapture(sys.argv[1])
while not cap.isOpened():
    print "Open video failed."
    sys.exit(-1)
ffmt=sys.argv[2]
i0=int(sys.argv[3])
i1=int(sys.argv[4])
skip=0
if len(sys.argv) > 5:
	skip = int(sys.argv[5])
wi=0
iskip=0
pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
while True:
    flag, frame = cap.read()
    if flag:
        # The frame is ready and already captured
        pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        if pos_frame >= i0:
			if iskip == skip:
				iskip=0
			elif skip != 0:
				iskip+=1
				continue
			cv2.imwrite(ffmt % wi, frame)
			print str(pos_frame)+" frames"
			wi+=1
			if wi >= i1:
				break
    else:
        # The next frame is not ready, so we try to read it again
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
        print "frame is not ready"
        # It is better to wait for a while for the next frame to be ready
        cv2.waitKey(1000)
    if cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
        # If the number of captured frames is equal to the total number of frames,
        # we stop
        break


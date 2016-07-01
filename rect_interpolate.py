import numpy as np
import scipy.interpolate
import sys, os
from util import *
import show_rect_rawoutput

def comp_overlay(r1, r2):
    x11 = r1[0]; x12 = r1[0] + r1[2]
    y11 = r1[1]; y12 = r1[1] + r1[3]
    x21 = r2[0]; x22 = r2[0] + r2[2]
    y21 = r2[1]; y22 = r2[1] + r2[3]
    a1 = r1[2]*r1[3]
    a2 = r2[2]*r2[3]
    x31=max(x11, x21); x32=min(x12, x22)
    y31=max(y11, y21); y32=min(y12, y22)
    iw=max(0, x32-x31)
    ih=max(0, y32-y31)
    ai=iw*ih
    return float(ai)/(a1+a2-ai)

def comp_similarity(r1, r2):
    center_dist = abs(r1[0]+r1[2]/2 - (r2[0]+r2[2]/2)) + abs(r1[1]+r1[3]/2 - (r2[1]+r2[3]/2))
    center_dist_ratio = float(center_dist) / (r1[2] + r1[3] + r2[2] + r2[3]) * 4 * 1.5
    w_diff_ratio = max(float(r1[2])/r2[2], float(r2[2])/r1[2]) - 1
    h_diff_ratio = max(float(r1[3])/r2[3], float(r2[3])/r1[3]) - 1
    return 1.0 / (center_dist_ratio + w_diff_ratio + h_diff_ratio + 1)

def rect2tracklets(rects2d):
    def linear_extrapolate_rect(track, target_frameid):
        if len(track) == 1:
            return track[-1][1:]
        else:
            rp2 = track[-2][1:]
            rp1 = track[-1][1:]
            x = float(target_frameid - track[-1][0]) / (track[-1][0] - track[-2][0])
            if x > 2: x = 2
            new_center_x = (rp1[0]+rp1[2]/2)*(1+x)-(rp2[0]+rp2[2]/2)*x
            new_center_y = (rp1[1]+rp1[3]/2)*(1+x)-(rp2[1]+rp2[3]/2)*x
            new_w = rp1[2]*(1+x)-rp2[2]*x
            new_h = rp1[3]*(1+x)-rp2[3]*x
            if new_h < 0: new_h = 1
            if new_w < 0: new_w = 1
            new_rect = [int(new_center_x-new_w/2), int(new_center_y-new_h/2), int(new_w), int(new_h)]
            return new_rect
    def find_most_similar_rects(target_rect, rects):
        maxid = -1; maxov = 0; i = 0
        for rect in rects:
            ov = comp_similarity(target_rect, rect)
            # ov = comp_overlay(track[-1][1:], rect)
            if ov > maxov:
                maxov = ov
                maxid = i
            i += 1
        return maxid, maxov
    options = {'overlay-th': 0.0,
        'similarity-th': 0.3,
        'frame-count-min': 1,
        'frame-interval-th': 20,
        }
    tracks = [] # [[(track1)[id1, r1]..] ..]
    track_predicts = [] # [(track1)[rect_predict] ..]
    frame_id = 0
    for rects in rects2d: # every frame
        if len(rects) > 0:
            for i in xrange(len(tracks)):
                track_predicts[i] = linear_extrapolate_rect(tracks[i], frame_id)
            neighber_rects = [track_predicts[i] for i in range(len(tracks)) if frame_id - options['frame-interval-th'] < tracks[i][-1][0]]
            # print "TRACK", tracks
            # print "PREDICT", track_predicts
            # print "NEIGHBER", neighber_rects
            # raw_input()
        for rectid, rect in enumerate(rects): # every rect
            searchid, ov = find_most_similar_rects(rect, neighber_rects)
            if searchid >= 0:
                trackid = track_predicts.index(neighber_rects[searchid])
            else:
                trackid = -1
            if ov > options['similarity-th']:
                maxrectid, ov = find_most_similar_rects(neighber_rects[searchid], rects)
                if maxrectid == rectid:
                    tracks[trackid].append([frame_id] + rect) # append tracklet
                else:
                    tracks.append([[frame_id] + rect]) # new tracklet
                    track_predicts.append([])
            else:
                tracks.append([[frame_id] + rect]) # new tracklet
                track_predicts.append([])
        frame_id += 1
    return tracks

def tracklets2rect(tracks):
    rectdict={}
    for tid, track in enumerate(tracks):
        for t in track:
            if rectdict.has_key(t[0]):
                rectdict[t[0]].append(t[1:] + [tid])
            else:
                rectdict[t[0]] = [t[1:] + [tid]]
    minfid=min(rectdict.keys())
    maxfid=max(rectdict.keys())
    rects=[]
    for i in xrange(maxfid+1):
        if i>=minfid and rectdict.has_key(i):
            rects.append([j for j in rectdict[i]])
        else:
            rects.append([])
    return rects

def interpolate_tracklets(tracks):
    new_tracks = []
    for track in tracks:
        nparr = np.array(track)
        if len(track) > 2:
            f_int = scipy.interpolate.interp1d(nparr[:,0], nparr[:,1:], kind='linear', axis=0)
        elif len(track) == 2:
            f_int = scipy.interpolate.interp1d(nparr[:,0], nparr[:,1:], kind='linear', axis=0)
        else:
            f_int = lambda i: nparr[0,1:]
        new_track = [([i] + f_int(i).tolist()) for i in xrange(track[0][0], track[-1][0]+1)]
        new_tracks.append(new_track)
    return new_tracks

def main():
    if len(sys.argv) < 4:
        print "Usage: interpolate.py labelpath imgroot rawrects"
        sys.exit(-1)
    rects = read_raw_rects(sys.argv[3])
    tracks = rect2tracklets(rects)
    tracks = interpolate_tracklets(tracks)
    rects_withtrack = tracklets2rect(tracks)
    # print rects_withtrack
    # show_rect_rawoutput.show(sys.argv[1], sys.argv[2], rects)
    show_rect_rawoutput.show(sys.argv[1], sys.argv[2], rects_withtrack)
    print len(tracks)

if __name__ == '__main__':
    main()

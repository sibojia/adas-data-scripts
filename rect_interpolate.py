import numpy as np
import scipy.interpolate
import sys, os
from util import *
import show_rect_rawoutput
import show_rect_rawoutput_video

options = {'overlay-th': 0.0,
    'similarity-th': 0.2,
    'frame-count-min': 10,
    'frame-interval-th': 25,
    'smooth-window-size-position': 7,
    'smooth-window-size-size': 11
    }

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
    if r1[2]<=0 or r1[3]<=0 or r2[2]<=0 or r2[3]<=0: return 0
    center_dist = abs(r1[0]+r1[2]/2 - (r2[0]+r2[2]/2)) + abs(r1[1]+r1[3]/2 - (r2[1]+r2[3]/2))
    center_dist_ratio = float(center_dist) / (r1[2] + r1[3] + r2[2] + r2[3]) * 4 * 2
    w_diff_ratio = max(float(r1[2])/r2[2], float(r2[2])/r1[2]) - 1
    h_diff_ratio = max(float(r1[3])/r2[3], float(r2[3])/r1[3]) - 1
    return 1.0 / (center_dist_ratio + w_diff_ratio + h_diff_ratio + 1)

def comp_color_similarity(img, r1, r2):
    def comp_ave_bgr(image, rect):
        s=rect[2]*rect[3]
        return [image[rect[1]:(rect[1]+rect[3]), rect[0]:(rect[0]+rect[2]), i].sum()/float(s) for i in [0,1,2]]
    def bgr2hue(b,g,r):
        # https://en.wikipedia.org/wiki/HSL_and_HSV
        alpha=0.5*(2*r-g-b)
        beta=1.732/2*(g-b)
        return np.arctan2(beta, alpha)
    h1 = bgr2hue(*comp_ave_bgr(img, r1))
    h2 = bgr2hue(*comp_ave_bgr(img, r2))
    return (np.pi - abs(h1-h2)) / np.pi

def rect2tracklets(imgs, rects2d):
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
            # make change in size smaller for prediction
            x = x / 2
            new_w = rp1[2]*(1+x)-rp2[2]*x
            new_h = rp1[3]*(1+x)-rp2[3]*x
            if new_h <= 0: new_h = 1
            if new_w <= 0: new_w = 1
            new_rect = [int(new_center_x-new_w/2), int(new_center_y-new_h/2), int(new_w), int(new_h)]
            return new_rect
    def find_most_similar_rects(img, target_rect, rects):
        maxid = -1; maxov = 0; i = 0
        for rect in rects:
            # ov = comp_color_similarity(img, target_rect, rect) * 0.2 + comp_similarity(target_rect, rect)
            ov = comp_similarity(target_rect, rect)
            # ov = comp_overlay(track[-1][1:], rect)
            if ov > maxov:
                maxov = ov
                maxid = i
            i += 1
        return maxid, maxov
    tracks = [] # [[(track1)[id1, r1]..] ..]
    track_predicts = [] # [(track1)[rect_predict] ..]
    frame_id = 0
    for rects in rects2d: # every frame
        # img = imgs[frame_id]
        img = None
        if len(rects) > 0:
            for i in xrange(len(tracks)):
                track_predicts[i] = linear_extrapolate_rect(tracks[i], frame_id)
            neighber_rects = [track_predicts[i] for i in range(len(tracks)) if frame_id - options['frame-interval-th'] < tracks[i][-1][0]]
            # print "TRACK", tracks
            # print "PREDICT", track_predicts
            # print "NEIGHBER", neighber_rects
            # raw_input()
        for rectid, rect in enumerate(rects): # every rect
            if rect[2] <= 0 or rect[3] <= 0:
                continue
            searchid, ov = find_most_similar_rects(img, rect, neighber_rects)
            if searchid >= 0:
                trackid = track_predicts.index(neighber_rects[searchid])
            else:
                trackid = -1
            if ov > options['similarity-th']:
                maxrectid, ov = find_most_similar_rects(img, neighber_rects[searchid], rects)
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

def remove_short_tracklets(tracks):
    new_tracks = []
    for track in tracks:
        if len(track) >= options['frame-count-min']:
            new_tracks.append(track)
    return new_tracks

def smooth_tracklets_moving_average(tracks):
    def running_mean(x, N):
        if N % 2 == 0: N += 1
        if x.shape[0] <= 2:
            return x
        elif x.shape[0] <= N:
            return running_mean(x, N-2)
        cumsum = np.cumsum(np.insert(x, 0, 0, axis = 0), axis = 0)
        x[(N-1)/2:-(N-1)/2] = (cumsum[N:] - cumsum[:-N]) / N
        for i in range((N-1)/2):
            x[i]=cumsum[i*2+1]/(i*2+1)
            # if i!=0: x[-i]=(cumsum[-1] - cumsum[-(i*2+2)])/(i*2+1)
        return x
    new_tracks = []
    for track in tracks:
        track_np = np.array(track)
        new_track_size = running_mean(track_np[:, 3:], options['smooth-window-size-size'])
        # This change position from left top to center
        track_np[:, 1] = track_np[:, 1] + track_np[:, 3]/2
        track_np[:, 2] = track_np[:, 2] + track_np[:, 4]/2
        # Different average window for position and size
        new_track_pos = running_mean(track_np[:, 1:3], options['smooth-window-size-position'])
        new_track_pos[:, 0] = new_track_pos[:, 0] - new_track_size[:, 0]/2
        new_track_pos[:, 1] = new_track_pos[:, 1] - new_track_size[:, 1]/2
        new_track = np.concatenate((track_np[:, 0:1], new_track_pos, new_track_size), axis = 1)
        new_tracks.append(new_track.astype(np.int32).tolist())
    return new_tracks

def smooth_tacklets_time_decay(tracks):
    def time_decay(x, K):
        memory_data = x[0,:]
        for i in xrange(x.shape[0]):
            x[i] = x[i] * K + memory_data * (1 - K)
            memory_data = x[i]
        return x
    new_tracks = []
    for track in tracks:
        track_np = np.array(track)
        track_np[:,1:3] = time_decay(track_np[:, 1:3], 0.8)
        track_np[:,3:5] = time_decay(track_np[:, 3:5], 0.6)
        new_tracks.append(track_np.astype(np.int32).tolist())
    return new_tracks

def main():
    if len(sys.argv) < 4:
        print "Usage: interpolate.py labelpath imgroot rawrects [output]"
        sys.exit(-1)
    rects = read_raw_rects(sys.argv[3])
    # imgs = read_all_images(sys.argv[1], sys.argv[2])
    imgs = []
    tracks = rect2tracklets(imgs, rects)
    tracks = interpolate_tracklets(tracks)
    tracks = smooth_tracklets_moving_average(tracks)
    rects_withtrack = tracklets2rect(tracks)
    # print rects_withtrack
    # show_rect_rawoutput.show(sys.argv[1], sys.argv[2], rects)
    if len(sys.argv) == 4:
        show_rect_rawoutput.show(sys.argv[1], sys.argv[2], rects_withtrack)
    else:
        dump_raw_rects(sys.argv[4], rects_withtrack, True)
    print len(tracks)

def main_video():
    if len(sys.argv) < 3:
        print "Usage: interpolate.py videopath rawrects [output_rawrects]"
        sys.exit(-1)
    rects = read_raw_rects(sys.argv[2])
    tracks = rect2tracklets(rects)
    tracks = interpolate_tracklets(tracks)
    tracks = remove_short_tracklets(tracks)
    rects_withtrack = tracklets2rect(tracks)
    # print rects_withtrack
    # show_rect_rawoutput.show(sys.argv[1], sys.argv[2], rects)
    if len(sys.argv) == 3:
        show_rect_rawoutput_video.show(sys.argv[1], rects_withtrack)
    else:
        dump_raw_rects(sys.argv[3], rects_withtrack, True)
    print len(tracks)

if __name__ == '__main__':
    main()

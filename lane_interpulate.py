#!/usr/bin/env python
import sys
import time
import select
import threading

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate
from util import *
import show_lanes

Y_LINSPACE = np.linspace(600, 1080, 80)

options = {'overlay-th': 0.0,
    'distance-th': 2000,
    'frame-count-min': 10,
    'frame-interval-th': 10,
    'smooth-forget-rate': 0.17
    }

def lines2tracklines(data):
    def find_nearest_line(line, lines):
        minid = -1
        mindis = 1e6
        i = 0
        length = len(Y_LINSPACE)/2
        for l in lines:
            s = sum([abs(x1-x2) for (x1,x2) in zip(line[length:], l[length:])])
            s /= length
            if s < mindis:
                minid = i
                mindis = s
            i += 1
        return minid, mindis
    tracks = []
    track_predicts = []
    frame_id = 0
    for lines in data: # frame
        lines_std = []
        for j in lines: # line
            px = np.array(j[0])
            py = np.array(j[1])
            if len(j[0]) == 2:
                z = np.polyfit(py, px, 1)
            else:
                z = np.polyfit(py, px, 3)
            p1 = np.poly1d(z)
            lines_std.append(p1(Y_LINSPACE))
        for lineid, j in enumerate(lines_std):
            minid, dis = find_nearest_line(j, track_predicts)
            # print minid, dis
            # raw_input()
            if dis < options['distance-th'] and tracks[minid][-1][0] > frame_id - options['frame-interval-th']:
                mintrackid, dis = find_nearest_line(track_predicts[minid], lines_std)
                if mintrackid == lineid:
                    tracks[minid].append([frame_id, min(lines[lineid][1]), max(lines[lineid][1])] + j.tolist())
                    track_predicts[minid] = j
                else:
                    tracks.append([[frame_id, min(lines[lineid][1]), max(lines[lineid][1])] + j.tolist()])
                    track_predicts.append(j)
            else:
                tracks.append([[frame_id, min(lines[lineid][1]), max(lines[lineid][1])] + j.tolist()])
                track_predicts.append(j)
        frame_id += 1
    return tracks

def lines2tracklines_naive(data):
    tracks = []
    previous_num = 0
    previous_start = 0
    frame_id = 0
    for lines in data: # frame
        lines_std = []
        # print 'lines', lines
        max_min_y = 0
        y_ind = 0
        for j in lines: # line
            px = np.array(j[0])
            py = np.array(j[1])
            if py.min() > max_min_y:
                max_min_y = py.min()
                for y_ind in xrange(80):
                    if Y_LINSPACE[y_ind] >= max_min_y: break
            if len(j[0]) == 2:
                z = np.polyfit(py, px, 1)
            else:
                z = np.polyfit(py, px, 3)
            p1 = np.poly1d(z)
            lines_std.append([frame_id, min(j[1]), max(j[1])] + p1(Y_LINSPACE).tolist())
        # print 'std', lines_std
        # print lines_std
        if frame_id > 500:
            lines_std.sort(key=lambda i:i[y_ind+10])
        else:
            lines_std.sort(key=lambda i:i[y_ind+5])

        # print lines_std
        # raw_input()
        # print 'sort', lines_std
        # raw_input()
        if len(lines_std) == 0 or (len(tracks) > 0 and tracks[previous_start][-1][0] > (frame_id - options['frame-interval-th']) and len(lines_std) == previous_num):
            keeptrack = True
        else:
            keeptrack = False
            previous_start = len(tracks)
            previous_num = len(lines_std)
        for lineid, j in enumerate(lines_std):
            if keeptrack:
                tracks[lineid + previous_start].append(j)
            else:
                tracks.append([j])
            # if (lineid + previous_start) >= len(tracks):
        # print keeptrack, len(tracks), previous_start, previous_num
        # raw_input()
        frame_id += 1
    return tracks

def smooth_tracks(tracks):
    new_tracks = []
    forget_rate = options['smooth-forget-rate']
    for track in tracks:
        if len(track) > 2:
            track_memory = track[0][1:]
            for frame_id in xrange(len(track)):
                for i in xrange(len(track_memory)):
                    if i < 2:
                        track[frame_id][i+1] = track[frame_id][i+1] * 0.02 + track_memory[i] * (1-0.02)
                    elif frame_id < 1035:
                        track[frame_id][i+1] = track[frame_id][i+1] * forget_rate + track_memory[i] * (1-forget_rate)
                    else:
                        track[frame_id][i+1] = track[frame_id][i+1] * 0.7 + track_memory[i] * 0.3
                    track_memory[i] = track[frame_id][i+1]
        new_tracks.append(track)
    return new_tracks

def tracklines2lines(tracks):
    linedict={}
    for tid, track in enumerate(tracks):
        for t in track:
            starti = 0; endi = 0
            for i, y in enumerate(Y_LINSPACE):
                if starti == 0 and y >= t[1]:
                    starti = i
                if endi == 0 and y >= t[2]:
                    endi = i
                    break
            if linedict.has_key(t[0]):
                linedict[t[0]].append([t[starti + 3: endi + 3], Y_LINSPACE[starti: endi].tolist(), tid])
            else:
                # print len(t), starti, endi
                linedict[t[0]] = [[t[starti + 3: endi + 3], Y_LINSPACE[starti: endi].tolist(), tid]]
                # print len(linedict[t[0]][0][0]), len(linedict[t[0]][0][1])
                # raw_input()
    minfid=min(linedict.keys())
    maxfid=max(linedict.keys())
    data=[]
    for i in xrange(maxfid+1):
        if i>=minfid and linedict.has_key(i):
            data.append(linedict[i])
        else:
            data.append([])
    return data

def main():
    data = read_lanes(sys.argv[1])
    # show_lanes.show_rawlines(data)
    tracks = lines2tracklines_naive(data)
    tracks = smooth_tracks(tracks)
    # print tracks[0]
    # raw_input()
    data_back = tracklines2lines(tracks)
    # show_lanes.show_rawlines(data_back)
    print len(tracks)
    dump_lanes("map_lane_stable.label", data_back)

if __name__ == "__main__":
    main()

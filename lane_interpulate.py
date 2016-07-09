#!/usr/bin/env python
import sys
import time
import select
import threading

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np
from util import *

Y_LINSPACE = np.linspace(600, 1100, 50)

options = {'overlay-th': 0.0,
    'distance-th': 500,
    'frame-count-min': 10,
    'frame-interval-th': 10,
    'smooth-forget-rate': 0.17
    }

def lines2tracklines(data):
    def find_nearest_line(line, lines):
        minid = -1
        mindis = 1e6
        i = 0
        for l in lines:
            s = sum([abs(x1-x2) for (x1,x2) in zip(line[20:], l[20:])])
            s /= len(Y_LINSPACE)
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

def smooth_tracks(tracks):
    new_tracks = []
    forget_rate = options['smooth-forget-rate']
    for track in tracks:
        if len(track) > 2:
            track_memory = track[0][3:]
            for frame_id in xrange(len(track)):
                for i in xrange(len(track_memory)):
                    track[frame_id][i+3] = track[frame_id][i+3] * forget_rate + track_memory[i] * (1-forget_rate)
                    track_memory[i] = track[frame_id][i+3]
        new_tracks.append(track)
    return new_tracks

def tracklines2lines(tracks):
    linedict={}
    for tid, track in enumerate(tracks):
        for t in track:
            starti = 0; endi = 0
            for i, y in enumerate(Y_LINSPACE):
                if starti == 0 and y > t[1]:
                    starti = i
                if endi == 0 and y > t[2]:
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

def show_rawlines(data):
    plt.gca().invert_yaxis()
    for i in data: # frame
        plt.gca().cla()
        plt.gca().axis([0, 1920, 1080, 0])
        for j in i: # line
            # print j
            # raw_input()
            plt.plot(j[0], j[1], '.', color='blue')
            px = np.array(j[0])
            py = np.array(j[1])
            if len(j[0]) == 2:
                z = np.polyfit(py, px, 1)
            else:
                z = np.polyfit(py, px, 3)
            p1 = np.poly1d(z)
            xp = np.linspace(min(j[1]), max(j[1]), 100)
            plt.plot(p1(xp), xp, '--')
        plt.draw()
        plt.pause(0.01)

def show_std_lines(data):
    plt.gca().invert_yaxis()
    for i in data: # frame
        plt.gca().cla()
        plt.gca().axis([0, 1920, 1080, 0])
        for j in i: # line
            plt.plot(j[:-1], Y_LINSPACE, '.', color='blue')
            # px = np.array(j[0])
            # py = np.array(j[1])
            # if len(j[0]) == 2:
            #     z = np.polyfit(py, px, 1)
            # else:
            #     z = np.polyfit(py, px, 3)
            # p1 = np.poly1d(z)
            # xp = np.linspace(min(j[1]), max(j[1]), 100)
            # plt.plot(p1(xp), xp, '--')
        plt.draw()
        plt.pause(0.01)

def main():
    data = read_lanes(sys.argv[1])


if __name__ == "__main__":
    data = read_lanes(sys.argv[1])
    # show_lines(data)
    tracks = lines2tracklines(data)
    tracks = smooth_tracks(tracks)
    # print tracks[0]
    # raw_input()
    data_back = tracklines2lines(tracks)
    # show_rawlines(data_back)
    print len(tracks)
    dump_lanes("lane_stable.label", data_back)
    # main()

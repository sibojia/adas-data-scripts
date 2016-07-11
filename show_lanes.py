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

def show_rawlines(data):
    plt.gca().invert_yaxis()
    for i in data: # frame
        plt.gca().cla()
        plt.gca().axis([0, 1920, 1080, 0])
        for j in i: # line
            plt.plot(j[0], j[1], '.', color='blue')
            px = np.array(j[0])
            py = np.array(j[1])
            if py[0] > py[-1]:
                px = px[::-1]
                py = py[::-1]
            # f_int = scipy.interpolate.interp1d(py, px, kind='linear')
            # tck = scipy.interpolate.splrep(py, px, s=1)
            if len(j[0]) == 2:
                z = np.polyfit(py, px, 1)
            elif len(j[0]) <= 10:
                z = np.polyfit(py, px, 3)
            else:
                z = np.polyfit(py, px, 3)
            yp = np.linspace(py.min(), py.max(), 100)
            # plt.plot(f_int(yp), yp, '.', color='red')
            # z = np.polyfit(yp, f_int(yp), 5)
            p1 = np.poly1d(z)
            # xp = scipy.interpolate.splev(yp, tck, der=0)
            plt.plot(p1(yp), yp, '--')
            # plt.plot(xp, yp, '--')
        plt.draw()
        plt.pause(0.01)

if __name__ == "__main__":
    data = read_lanes(sys.argv[1])
    show_rawlines(data)

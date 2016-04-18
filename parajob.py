#!/usr/bin/python

import os
import threading
import glob


def parajob():
    caldirs = glob.glob('paraCal*')
    numthread = len(caldirs)
    runs = []
    for i in range(numthread):
        runs.append(threading.Thread(target=execvasp, args=(caldirs[i],)))
    for t in runs:
        t.start()
    for t in runs:
        t.join()


def execvasp(caldir):
    os.system("cd " + caldir + ";sh runvasp.sh")


if __name__ == '__main__':
    parajob()
    print 'FINISHED'

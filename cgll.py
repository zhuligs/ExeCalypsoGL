#!/usr/bin/python -u
# encoding: utf-8

# *****************************************************************************
# Copyright (C) 2016 Li Zhu
# All rights reserved.
#
# cgll.py
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# *****************************************************************************

import os
import time
import cPickle as pick
import glob
import subprocess

# optimized for DOD cluster


def pushlocal(istep, npop):
    """push geometry opt local
    :returns: TODO

    """
    # os.system('mkdir step' + str(istep))
    # os.system('cp POSCAR_* step' + str(istep))
    subprocess.call(["mkdir", "data" + str(istep)])
    subprocess.call(["cp", "POSCAR_*", "data" + str(istep)])
    idpool = []
    for i in range(npop):
        ip = str(i + 1)
        cdir = 'Cal/' + ip
        # os.system('mkdir -p ' + cdir)
        subprocess.call(["mkdir", "-p", cdir])
        subprocess.call(["cp", "POSCAR_" + ip, cdir + "/POSCAR"])
        subprocess.call(["cp", "INCAR_*", "POTCAR", "pbs.sh", cdir])
        # os.system('cp POSCAR_' + ip + ' ' + cdir + '/POSCAR')
        # os.system('cp INCAR_* POTCAR pbs.sh ' + cdir)
        # jbuff = os.popen('cd ' + cdir + '; qsub pbs.sh').read()
        jbuff = subprocess.check_output(["cd", cdir + ";", "qsub", "pbs.sh"])
        jid = jbuff.strip()
        idpool.append(jid)

    f = open('idpool.dat', 'w')
    pick.dump(idpool, f)
    f.close()
    return idpool


def checkjob(idpool):

    while True:
        try:
            jbuff = subprocess.check_output(["qstat", "-u", "zhuli"])
            break
        except:
            time.sleep(2)

    if len(jbuff.strip()) > 0:
        kbuff = jbuff.strip().split('\n')
        reminds = []
        try:
            for x in kbuff[2:]:
                reminds.append(x.split()[0])
        except:
            return True
    else:
        return True
    finished = True
    for id in idpool:
        if id in reminds:
            finished = False
    return finished


def pulllocal(istep, npop):
    for i in range(npop):
        ip = str(i + 1)
        cdir = 'Cal/' + ip
        while True:
            try:
                subprocess.call(["cp", cdir + "/CONTCAR", "CONTCAR_" + ip])
                subprocess.call(["cp", cdir + "/OUTCAR", "OUTCAR_" + ip])
                break
            except:
                time.sleep(2)
        if checkcontcar('CONTCAR_' + ip):
            subprocess.call(["cp", "POSCAR_" + ip, "CONTCAR_" + ip])
    subprocess.call(["mkdir", "-p", "data" + str(istep)])
    subprocess.call(["cp", "POSCAR_*", "OUTCAR_*", "CONTCAR_*",
                     "data" + str(istep)])


def checkcontcar(contcar):
    buff = subprocess.check_output(["du", contcar])
    jbuff = int(buff.split()[0])
    if jbuff == 0:
        return True
    else:
        return False


def newjob(kstep, maxstep, npop):
    for istep in range(kstep, maxstep + 1):
        print 'ISTEP', istep
        subprocess.call(["./calypso.x", ">>CALYPSO.STDOUT"])
        cglstatus = 0
        dumpgcl(cglstatus)
        idpool = pushlocal(istep, npop)
        print 'idpool', idpool
        cglstatus = 1
        dumpgcl(cglstatus)
        finished = False
        while not finished:
            if checkjob(idpool):
                pulllocal(istep, npop)
                finished = True
                print 'OPT FINISHED', istep
            print 'OPT NOT YET FINISH', istep
            time.sleep(30)
        cglstatus = 2
        dumpgcl(cglstatus)


def dumpgcl(cglstatus):
    f = open('cgls.dat', 'w')
    pick.dump(cglstatus, f)
    f.close()


def loadgcl():
    f = open('cgls.dat')
    cglstatus = pick.load(f)
    f.close()
    return cglstatus


def readinput():
    finput = 'input.dat'
    indata = {}
    f = open(finput, 'r')
    for line in f:
        if '=' in line:
            if line.strip()[0] != '#':
                litem = line.split('=')
                indata[litem[0].strip().lower()] = litem[1].strip()
    f.close()

    npop = int(indata['popsize'])
    try:
        systemname = indata['systemname']
    except:
        systemname = 'CALY'

    maxstep = int(indata['maxstep'])

    return(systemname, npop, maxstep)


def restartjob(kstep, maxstep, npop):

    cglstatus = loadgcl()
    if cglstatus == 0:
        idpool = pushlocal(kstep, npop)
        cglstatus = 1
        dumpgcl(cglstatus)
        finished = False
        while not finished:
            if checkjob(idpool):
                pulllocal(kstep, npop)
                finished = True
                print 'OPT FINISHED', kstep
            time.sleep(30)
            print 'OPT NOT YET FINISHED'
        cglstatus = 2
        dumpgcl(cglstatus)
    elif cglstatus == 1:
        f = open('idpool.dat')
        idpool = pick.load(f)
        f.close()
        finished = False
        while not finished:
            if checkjob(idpool):
                pulllocal(kstep, npop)
                finished = True
                print 'OPT FINISHED', kstep
            print 'OPT NOT YET FINISHED'
            time.sleep(30)
        cglstatus = 2
        dumpgcl(cglstatus)
    elif cglstatus == 2:
        os.system('cp data' + str(kstep) + '/* .')

    newjob(kstep + 1, maxstep, npop)


def check_status():
    lstep = glob.glob('step')
    if lstep == []:
        restart = False
        kstep = 1
    else:
        restart = True
        buff = os.popen('cat step').read()
        kstep = int(buff.strip())
    return (restart, kstep)


def cgl():
    (systemname, npop, maxstep) = readinput()
    # bdir = 'CGL/' + systemname
    (restart, kstep) = check_status()
    if restart:
        print 'RESTART JOB'
        restartjob(kstep, maxstep, npop)
    else:
        print 'NEW JOB'
        newjob(kstep, maxstep, npop)
    return 0


if __name__ == "__main__":
    # print checkjob([996705])
    # print checkjob([234])
    cgl()











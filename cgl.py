#!/usr/bin/python

# Copyright (C) 2015 Li Zhu
# All rights reserved.

import numpy as np
import os
import time
import cPickle as pick
import glob

def pushjob(istep, npop, bdir):
    # os.system('./calypso.x >> CALYPSO.STDOUT')
    # os.system('scp POSCAR_* INCAR_* POTCAR accc:/home/jtse/prin/' + rdir)
    os.system('mkdir step' + str(istep))
    os.system('cp POSCAR_* step' + str(istep))
    idpool = []
    for i in range(npop):
        ip = str(i + 1)
        # rdir = 'cgl/' + systemname + ip
        rdir = bdir + '/' + ip
        os.system('ssh accc mkdir -p ' + rdir)
        # os.system('ssh accc rm rdir/*')
        os.system('scp POSCAR_' + ip + ' ' + rdir + '/POSCAR')
        os.system('scp INCAR_* POTCAR pbs.sh' + rdir)
        jbuff = os.popen('sh elite.sh').read()
        jid = int(jbuff.split()[5])
        idpool.append(jid)

    f = open('idpool.dat', 'w')
    pick.dump(idpool, f)
    f.close()
    return idpool

def checkjob(idpool):
    jbuff = os.popen('ssh accc pjstat').read()
    kbuff = jbuff.split('\n')
    remids = []
    if len(kbuff[6].strip()) > 0:
        for x in kbuff[6:-1]:
            remids.append(int(x.split()[0]))
    else:
        return True

    finished = True
    for id in idpool:
        if id in remids:
            finished = False

    return finished

def pulljob(bdir, npop):
    for i in range(npop):
        ip = str(i + 1)
        rdir = bdir + '/' + ip
        os.system('scp accc:' + rdir + '/CONTCAR CONTCAR_' + ip)
        os.system('scp accc:' + rdir + '/OUTCAR OUTCAR_' + ip)
        if checkcontcar('CONTCAR_' + ip):
            os.system('cp POSCAR_' + ip + ' CONTCAR_' + ip)
    os.system('mkdir -p data' + ip)
    os.system('cp POSCAR_* CONTCAR_* OUTCAR_* data' + ip)


def checkcontcar(contcar):
    buff = os.popen('du ' + contcar).read()
    jbuff = int(buff.split()[0])
    if jbuff == 0:
        return True
    else:
        return False

def newjob(bdir, kstep):
    for istep in range(kstep, maxstep):
        os.system('./calypso.x >> CALYPSO.STDOUT')
        cglstatus = 0
        idpool = pushjob(istep, npop, bdir)
        finished = False
        while not finished:
            if checkjob(idpool):
                pulljob(bdir)
            time.sleep(1)

def restartjob(bdir, kstep):
    f = open('idpool.dat')
    idpool = pick.load(f)
    f.close()

    newjob(bdir, kstep)


def check_status():
    lstep = glob.glob('step')
    if lstep == []:
        restart = False
        kstep = 0
    else:
        restart = True
        buff = os.popen('cat step').read()
        kstep = int(buff.strip())
    return (restart, kstep)


def cgl():
    bdir = 'cgl/' + systemname
    (restart, kstep) = check_status()
    if restart:
        restartjob(bdir, kstep)
    else:
        newjob(bdir, kstep)
    return 0

if __name__ == "__main__":
    # print checkjob([996705])
    # print checkjob([234])
    pulljob('/home/jtse/prin/cp', 5)



#!/usr/bin/python -u

# Copyright (C) 2015 Li Zhu
# All rights reserved.

import os
import time
import cPickle as pick
import glob


def pushjob(istep, npop, bdir):
    os.system('mkdir step' + str(istep))
    os.system('cp POSCAR_* step' + str(istep))
    idpool = []
    for i in range(npop):
        ip = str(i + 1)
        # rdir = 'cgl/' + systemname + ip
        rdir = bdir + '/' + ip
        while True:
            stat0 = os.system('ssh accc mkdir -p ' + rdir)
            if stat0 == 0:
                break
            else:
                time.sleep(2)
        # os.system('ssh accc rm rdir/*')
        while True:
            stat0 = os.system('scp POSCAR_' + ip + ' accc:' + rdir + '/POSCAR')
            if stat0 == 0:
                break
            else:
                time.sleep(2)
        while True:
            stat0 = os.system('scp INCAR_* POTCAR pbs.sh' + ' accc:' + rdir)
            if stat0 == 0:
                break
            else:
                time.sleep(2)
        fe = open('elite.sh', 'w')
        fe.write('#!/bin/sh\n')
        fe.write('ssh accc << !\n')
        fe.write('cd ' + rdir + '\n')
        fe.write('pjsub pbs.sh\n')
        fe.write('!\n')
        fe.close()
        while True:
            jbuff = os.popen('sh elite.sh').read()
            if len(jbuff.strip()) != 0:
                break
            else:
                time.sleep(2)
        jid = int(jbuff.split()[5])
        idpool.append(jid)

    f = open('idpool.dat', 'w')
    pick.dump(idpool, f)
    f.close()
    return idpool


def checkjob(idpool):
    while True:
        jbuff = os.popen('ssh accc pjstat').read()
        if len(jbuff.strip()) != 0:
            break
        else:
            time.sleep(2)
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


def pulljob(bdir, npop, istep):
    for i in range(npop):
        ip = str(i + 1)
        rdir = bdir + '/' + ip
        while True:
            stat0 = os.system('scp accc:' + rdir + '/CONTCAR CONTCAR_' + ip)
            if stat0 == 0:
                break
            else:
                time.sleep(2)
        while True:
            stat0 = os.system('scp accc:' + rdir + '/OUTCAR OUTCAR_' + ip)
            if stat0 == 0:
                break
            else:
                time.sleep(2)
        if checkcontcar('CONTCAR_' + ip):
            os.system('cp POSCAR_' + ip + ' CONTCAR_' + ip)
    os.system('mkdir -p data' + str(istep))
    os.system('cp POSCAR_* CONTCAR_* OUTCAR_* data' + str(istep))


def checkcontcar(contcar):
    buff = os.popen('du ' + contcar).read()
    jbuff = int(buff.split()[0])
    if jbuff == 0:
        return True
    else:
        return False


def newjob(bdir, kstep, maxstep, npop):
    for istep in range(kstep, maxstep + 1):
        print 'ISTEP', istep
        os.system('./calypso.x >> CALYPSO.STDOUT')
        cglstatus = 0
        dumpgcl(cglstatus)
        idpool = pushjob(istep, npop, bdir)
        print 'idpool', idpool
        cglstatus = 1
        dumpgcl(cglstatus)
        finished = False
        while not finished:
            if checkjob(idpool):
                pulljob(bdir, npop, istep)
                finished = True
                print 'OPT FINISHED', istep
            print 'OPT NOT YET FINISHED', istep
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


def restartjob(bdir, kstep, maxstep, npop):

    cglstatus = loadgcl()
    if cglstatus == 0:
        idpool = pushjob(kstep, npop, bdir)
        cglstatus = 1
        dumpgcl(cglstatus)
        finished = False
        while not finished:
            if checkjob(idpool):
                pulljob(bdir, npop, kstep)
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
                pulljob(bdir, npop, kstep)
                finished = True
                print 'OPT FINISHED', kstep
            print 'OPT NOT YET FINISHED'
            time.sleep(30)
        cglstatus = 2
        dumpgcl(cglstatus)
    elif cglstatus == 2:
        os.system('cp data' + str(kstep) + '/* .')

    newjob(bdir, kstep + 1, maxstep, npop)


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


def cgl():
    (systemname, npop, maxstep) = readinput()
    bdir = 'CGL/' + systemname
    (restart, kstep) = check_status()
    if restart:
        print 'RESTART JOB'
        restartjob(bdir, kstep, maxstep, npop)
    else:
        print 'NEW JOB'
        newjob(bdir, kstep, maxstep, npop)
    return 0


if __name__ == "__main__":
    # print checkjob([996705])
    # print checkjob([234])
    cgl()

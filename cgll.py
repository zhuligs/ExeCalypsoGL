#!/usr/bin/python -u
# encoding: utf-8

# Copyright (C) 2016 Li Zhu
# All rights reversed.

import os
import time
import cPickle as pick
import glob

def pushlocal(istep, npop, bdir):
    """push geometry opt local
    :returns: TODO

    """
    os.system('mkdir step' + str(istep))
    os.system('cp POSCAR_* step' + str(istep))
    idpool = []
    for i in range(npop):
        ip = str(i + 1)
        cdir = 'Cal/' + ip
        os.system('mkdir -p ' + cdir)
        os.system('cp POSCAR_' + ip + ' ' + cdir + '/POSCAR')
        os.system('cp INCAR_* POTCAR pbs.sh ' + cdir)
        jbuff = os.popen('cd ' + cdir + '; qsub pbs.sh').read()
        jid = jbuff.strip()
        idpool.append(jid)

    f = open('idpool.dat', 'w')
    pick.dump(idpool, f)
    f.close()
    return idpool


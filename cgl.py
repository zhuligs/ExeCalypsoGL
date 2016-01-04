#!/usr/bin/python

# Copyright (C) 2015 Li Zhu 
# All rights reserved. 

import numpy as np
import os
import glob

def cgl():
    os.system('./calypso.x >> CALYPSO.STDOUT') 
    #os.system('scp POSCAR_* INCAR_* POTCAR accc:/home/jtse/prin/' + rdir)
    for i in range(npop):
        ip = str(i + 1)
        rdir = 'cgl/' + systemname + ip
        os.system('ssh accc mkdir -p ' + rdir)
        os.system('scp POSCAR_' + ip + ' ' + rdir)

    




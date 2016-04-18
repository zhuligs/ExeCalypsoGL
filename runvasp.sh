#!/bin/bash

cp INCAR_1 INCAR
python /home/lzhu/apps/writekp.py 0.12
mpiexec -machinefile hosts.sp -n 24 /home/lzhu/apps/vasp.5.4.1/bin/vasp_std > log
cp OUTCAR OUTCAR_1
cp CONTCAR CONTCAR_1
cp CONTCAR POSCAR

cp INCAR_2 INCAR
python /home/lzhu/apps/writekp.py 0.12
mpiexec -machinefile hosts.sp -n 24 /home/lzhu/apps/vasp.5.4.1/bin/vasp_std > log
cp OUTCAR OUTCAR_2
cp CONTCAR CONTCAR_2
cp CONTCAR POSCAR

cp INCAR_3 INCAR
python /home/lzhu/apps/writekp.py 0.08
mpiexec -machinefile hosts.sp -n 24 /home/lzhu/apps/vasp.5.4.1/bin/vasp_std > log
cp OUTCAR OUTCAR_3
cp CONTCAR CONTCAR_3
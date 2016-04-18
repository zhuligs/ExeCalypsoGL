#!/bin/bash
#PBS -l nodes=6:ppn=24
#PBS -l walltime=00:30:00
#PBS -N TEMPNAME

cd "$PBS_O_WORKDIR"

srun hostname -s |sort > hosts
uniq hosts > shost
sed -i 's/$/.local/' hosts
sed -i 's/$/.local/' shost

#alldo killall python
A=`cat shost`
for x in $A
do
    ssh $x killall python
done

mpdboot -n 6 --verbose -r /usr/bin/ssh -f shost
##
#mpiexec -machinefile hosts -n 48 /home/lzhu/apps/vasp.5.4.1/bin/vasp_std > log

split -d -l 24 hosts

for i in 0 1 2 3 4 5
do
    cp x0$i paraCal$i/hosts.sp 
done

python parajob.py

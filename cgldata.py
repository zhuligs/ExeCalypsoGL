jobpool = []
maxcalyrun = 5
xdirs = []

inputtemplate = '''SystemName = TEMP_SN
NumberOfSpecies = TEMP_NOS
NameOfAtoms = TEMP_NOA
AtomicNumber =  TEMP_AN
NumberOfAtoms =  TEMP_NA
NumberOfFormula = TEMP_NOF
Volume = TEMP_VOL
Ialgo = 2
PsoRatio = 0.6
Split = T
PopSize = TEMP_PS
ICode = 1
NumberOfLbest = 4
NumberOfLocalOptim = 3
Kgrid = 0.12 0.08
Command = sh submit.sh
GenType = 1
MaxStep = TEMP_MS
'''

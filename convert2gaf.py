#!/usr/bin/python

from sys import argv as sys_argv
from sys import exit as sys_exit

try:
    inp_file = sys_argv[1]
    out_file = sys_argv[2]
except:
    print "USAGE: \n  convert2gaf.py name_of_input_file name_of_output_file \n e.g. \n convert2gaf.py Wenner.dat Wenner_gaf.dat \n\n"
    sys_exit()

inp = open(inp_file,'r')
out = open(out_file,'w')

# Name of survey line
line = inp.readline()
out.write(line)

# Unit electrode spacing
spac = inp.readline()
out.write(spac.lstrip())

# Array type (11 for general array)
intype = int(inp.readline()) # 1-Wenner, 3-Dipole-Dipole, 7-Schlumberger
out.write('11\r\n')

# Array type, 0 non-specific
out.write('0\r\n')

# Header
out.write('Type of measurement (0=app. resistivity,1=resistance)\r\n')
out.write('0\r\n') # to indicate app. resistivity

# Number of data points
numdata = inp.readline()
out.write(numdata.lstrip())
numdata = int(numdata)

# Type of x-location for data points, 1 for mid-point
line = inp.readline()
if line == 1: 
    stop
out.write('2\r\n') # 0-no topography, 1-true horizontal distance, 2-ground distance


# Flag for I.P. data, 0 for none (1 if present)
line = inp.readline()
out.write(line)

# Data Points
for i in range(numdata):
    line = inp.readline()
    line = line.split()
    x0   = float(line[0])
    a    = float(line[1])
    if intype == 1:
        res  = float(line[2])
    else:
        n    = float(line[2])
        res  = float(line[3])
    C1   = x0
    if intype == 1: # Wenner
        C2   = x0 + 3*a
        P1   = x0 +   a
        P2   = x0 + 2*a
    elif intype == 3: # Dipole-Dipole
        C2   = x0 + a
        P1   = x0 + a*(n+1)
        P2   = x0 + a*(n+2)
    elif intype == 7: # Schlumberger
        C2   = x0 + a*(2*n+1)
        P1   = x0 + a*n
        P2   = x0 + a*(n+1)
    out.write('4 {0:.4f} 0.0000 {1:.4f} 0.0000 {2:.4f} 0.0000 {3:.4f} 0.0000 {4:.4f}\r\n'.format(C1,C2,P1,P2,res))

for i in range(5):
    out.write('0\r\n')

inp.close()
out.close()

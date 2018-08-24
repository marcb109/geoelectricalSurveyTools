#!/usr/bin/python

from sys import argv as sys_argv
from sys import exit as sys_exit
import os

try:
    out_file = sys_argv[1]
    inp_file = sys_argv[2]
    if len(sys_argv) > 3:
        ohm_file = sys_argv[3]
        topography = True
except:
    print "USAGE: \n  convertmod2vtk.py output_file input_file [ohm_file_for_topography] \n e.g. \n convertmod2vtk.py Wenner.vtk Wenner.mod Wenner.ohm\n\n"
    sys_exit()

# read mod file
inp = open(inp_file,'r')
lines = inp.readlines()
inp.close()
del lines[0] # delete header line (#x1/m	x2/m	z1/m	z2/m	rho/Ohmm coverage)
x = []
z = []
rho = []
coverage = []
for line in lines:
    tmp = line.split()
    x.append([float(tmp[0]),float(tmp[1])])
    z.append([-float(tmp[2]),-float(tmp[3])])
    rho.append(float(tmp[4]))
    coverage.append(float(tmp[5]))

# read ohm file
if topography:
    ohm = open(ohm_file,'r')
    lines = ohm.readlines()
    ohm.close()
    index = lines.index('# x h for each topo point\r\n')
    num_topopoints = int(lines[index-1].split('#')[0])
    lines = lines[index+1:]
    x_topo = []
    z_topo = []
    for line in lines:
        tmp = line.split()
        x_topo.append(float(tmp[0]))
        z_topo.append(float(tmp[1]))
    topo = dict(zip(x_topo,z_topo))

# some calculations
num_cells = len(rho)
points = []
cells = []
for i in range(num_cells):
    cell = []
    for j in range(2):
        for k in range(2):
            point = [x[i][j],0.0,z[i][k]]
            try:
                index = points.index(point)
                cell.append(index)
            except:
                points.append(point)
                cell.append(len(points)-1)
    index = cell[2]
    cell[2] = cell[3]
    cell[3] = index
    cells.append(cell)
num_points = len(points)

if topography:
    for point in points:
        if point[0] in topo:
            point[2] += topo[point[0]]
        else:
            #use nearest topography point
            point[2] += topo[min(topo.keys(), key=lambda k: abs(k-point[0]))]

# write VTK file
out = open(out_file,'w')
out.write('# vtk DataFile Version 3.0\n')
out.write(os.path.split(inp_file)[1]+'\n')
out.write('ASCII\n')

out.write('DATASET UNSTRUCTURED_GRID\n')
out.write('POINTS {0:d} float\n'.format(num_points))
for point in points:
    out.write(' '.join(str(x) for x in point)+'\n')
out.write('CELLS {0:d} {1:d}\n'.format(num_cells,num_cells*5))
for cell in cells:
    out.write('4 '+' '.join(str(i) for i in cell)+'\n')
out.write('CELL_TYPES {0:d}\n'.format(num_cells))
for cell in cells:
    out.write('9\n')
out.write('\n')
out.write('CELL_DATA '+str(num_cells)+'\n')
out.write('SCALARS rho float 1\n')
out.write('LOOKUP_TABLE default\n')
for value in rho:
    out.write('{0}\n'.format(value))
out.write('SCALARS coverage float 1\n')
out.write('LOOKUP_TABLE default\n')
for value in coverage:
    out.write('{0}\n'.format(value))
out.close()

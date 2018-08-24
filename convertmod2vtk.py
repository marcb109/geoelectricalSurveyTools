#!/usr/bin/env python3

from sys import argv as sys_argv
from sys import exit as sys_exit
import os
import numpy as np


class Point3D:

    def __init__(self, x, y, z):
        """

        :param x: first horizontal coordinate
        :param y: second horizontal coordinate
        :param z: vertical coordinate
        """
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        # make class iterable by returning x, then y then z coordinate
        return iter((self.x, self.y, self.z))

    def __eq__(self, other):
        # Compare two points, return true if they have the same coordinates
        return self.x == other.x and self.y == other.y and self.z == other.z


def convert(startpoint, endpoint, numpoints, spacing):
    """

    :param spacing: Abstand zwischen den Elektroden (z.B. 2, 4) (m)
    :type spacing:
    :param startpoint: Koordinaten der ersten Elektrode in UTM (m)
    :type startpoint:
    :param endpoint: Koordinaten der letzten Elektrode in UTM (m)
    :type endpoint:
    :param numpoints:
    :type numpoints: Anzahl der Elektroden
    :return:
    :rtype:
    """
    x_interpolated = np.linspace(startpoint[0], endpoint[0], numpoints)
    y_interpolated = np.linspace(startpoint[1], endpoint[1], numpoints)
    x_old = []
    for i in range(numpoints):
        x_old.append(float(i*spacing))
    int_coord = {}
    for j in range(numpoints):
        int_coord[x_old[j]] = (x_interpolated[j], y_interpolated[j])
    distance_x = x_interpolated[0] - x_interpolated[1]
    distance_y = y_interpolated[0] - y_interpolated[1]
    int_coord[-spacing] = [int_coord[0][0] -distance_x, int_coord[0][1] - distance_y]
    int_coord[(numpoints)*spacing] = [int_coord[(numpoints-1)*spacing][0] - distance_x, int_coord[(numpoints-1)*spacing][1] - distance_y]

    return int_coord

def convertmod2vtk(out_file, inp_file, ohm_file=None):

    # only use topography if ohm file is given
    topography = ohm_file is not None

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
        # x holds x1 x2 pair of coordinates
        x.append([float(tmp[0]),float(tmp[1])]) ###?
        # z holds z1 z2 pair of coordinates
        z.append([-float(tmp[2]),-float(tmp[3])])
        # measured specific resistivity
        rho.append(float(tmp[4]))
        # coverage is how often a block was targeted during measurement. Higher coverage -> more confident result
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
            x_topo.append(float(tmp[0])) ###
            z_topo.append(float(tmp[1])) ###
        topo = dict(zip(x_topo,z_topo))

    # some calculations
    num_cells = len(rho)
    points = []
    cells = []
    for i in range(num_cells):
        cell = []
        for j in range(2):
            for k in range(2):
                # second coordinate is y , which is the horizontal deviation perpendicular to the the straight profile
                point = Point3D(x[i][j], 0.0, z[i][k])
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
            if point.x in topo:
                point.z += topo[point.x]
            else:
                #use nearest topography point
                point.z += topo[min(topo.keys(), key=lambda k: abs(k-point.x))]

    startpoint = (356933, 5686395)
    endpoint = (357127, 5686380)
    numpoints = 50
    spacing = 4

    converted_points = convert(startpoint, endpoint, numpoints, spacing)

    for point in points:
        point.x, point.y = converted_points[point.x]

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

if __name__ == '__main__':
    try:
        out_file = sys_argv[1]
        inp_file = sys_argv[2]
        if len(sys_argv) > 3:
            ohm_file = sys_argv[3]
        else:
            ohm_file = None
    except:
        print("USAGE: \n  convertmod2vtk.py output_file input_file [ohm_file_for_topography] \n e.g. \n convertmod2vtk.py Wenner.vtk Wenner.mod Wenner.ohm\n\n")
        sys_exit()

    convertmod2vtk(out_file, inp_file, ohm_file)
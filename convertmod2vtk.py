#!/usr/bin/env python3
import argparse
import os
from math import atan2, cos, sin
import itertools

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

    def __sub__(self, other):
        return Point3D(self.x-other.x, self.y-other.y, self.z-other.z)

    def __repr__(self):
        return "Point3D({x}, {y}, {z})".format(x=self.x, y=self.y, z=self.z)


def convert_relative_to_utm(startpoint, endpoint, relative_distance):
    """
    Convert spacing along a line from startpoint to endpoint, which is measured relative to startpoint to UTM
    coordinates.
    :param startpoint: UTM coordinate (m) of start point
    :type startpoint: Point3D
    :param endpoint: UTM coordinate (m) of end point
    :type endpoint: Point3D
    :param relative_distance: Spacing from start point along the line to endpoint at which a new UTM coordinate
    should be calculated
    :type relative_distance: float
    :return: UTM coordinate Point which is at the distance relative_distance from startpoint. New UTM coordinate is
    interpolated.
    :rtype: Point3D
    """
    connecting_vector = endpoint - startpoint
    angle_radians = atan2(connecting_vector.y, connecting_vector.x)
    dx = cos(angle_radians) * relative_distance
    dy = sin(angle_radians) * relative_distance
    return Point3D(startpoint.x + dx, startpoint.y + dy, startpoint.z)

def read_mod_file(mod_filename):
    # read mod file
    inp = open(mod_filename, 'r')
    lines = inp.readlines()
    inp.close()
    del lines[0]  # delete header line (#x1/m	x2/m	z1/m	z2/m	rho/Ohmm coverage)

    # convert list of strings to list of lists of float
    lines = [[float(number) for number in line.split()] for line in lines]
    # x holds x1 x2 pair of coordinates
    x = [[line[0], line[1]] for line in lines]
    # z holds z1 z2 pair of coordinates
    z = [[-line[2], -line[3]] for line in lines]
    # measured specific resistivity
    rho = [line[4] for line in lines]
    # coverage is how often a block was targeted during measurement. Higher coverage -> more confident result
    coverage = [line[5] for line in lines]
    return x, z, rho, coverage

def read_ohm_file(ohm_filename):
    # read ohm file
    ohm = open(ohm_filename, 'r')
    lines = ohm.readlines()
    ohm.close()
    # remove file all lines without data
    index = lines.index('# x h for each topo point\r\n')
    lines = lines[index+1:]
    #num_topopoints = int(lines[index-1].split('#')[0])
    # convert list of strings to list of lists of float
    lines = [[float(number) for number in line.split()] for line in lines]
    x_topo = [line[0] for line in lines]
    z_topo = [line[1] for line in lines]
    topo = dict(zip(x_topo, z_topo))
    return topo

def create_geometry(x_coordinate_pair, z_coordinate_pair):
    """
    Create list of unique points and list of cells from those points
    :param x_coordinate_pair: list of x1,x2 coordinate pairs
    :type x_coordinate_pair: list of floats
    :param z_coordinate_pair: list of z1,z2 coordinate pairs
    :type z_coordinate_pair: list of floats
    :return:
    points: list of unique points built from all four combinations
    cells: list of cells built by these points. A cell is a list that saves the indices of its edges in the points list.
    """
    points = []     # list of all unique points read from vtk file
    cells = []      # list of lists, every sublists contains indices of points of a cell in points list
    for x_pair, z_pair in zip(x_coordinate_pair, z_coordinate_pair):
        cell = []   # list that holds the index of corner points of the cell
        # loop over all x,z combinations
        for x, z in itertools.product(x_pair, z_pair):
            # second coordinate is y, which is the horizontal deviation perpendicular to the the straight profile
            point = Point3D(x, 0.0, z)
            try:
                # successful if created point is already in list of points
                index = points.index(point)
            except ValueError:
                # point is not in list of points, append it
                index = len(points)
                points.append(point)
            cell.append(index)
        # swap content of cell 2/3    WHY???
        cell[2], cell[3] = cell[3], cell[2]
        cells.append(cell)
    return points, cells

def write_vtk_file(vtk_filename, input_filename, points, cells, rho, coverage):
    num_points = len(points)
    num_cells = len(cells)
    # write VTK file
    with open(vtk_filename, 'w') as out:
        # write header
        out.write('# vtk DataFile Version 3.0\n')
        out.write(input_filename + '\n')
        out.write('ASCII\n')

        out.write('DATASET UNSTRUCTURED_GRID\n')
        out.write('POINTS {0:d} float\n'.format(num_points))
        # write data
        for point in points:
            out.write(' '.join(str(x) for x in point) + '\n')
        out.write('CELLS {0:d} {1:d}\n'.format(num_cells, num_cells * 5))
        for cell in cells:
            out.write('4 ' + ' '.join(str(i) for i in cell) + '\n')
        out.write('CELL_TYPES {0:d}\n'.format(num_cells))
        for cell in cells:
            out.write('9\n')
        out.write('\n')
        out.write('CELL_DATA ' + str(num_cells) + '\n')
        out.write('SCALARS rho float 1\n')
        out.write('LOOKUP_TABLE default\n')
        for value in rho:
            out.write('{0}\n'.format(value))
        out.write('SCALARS coverage float 1\n')
        out.write('LOOKUP_TABLE default\n')
        for value in coverage:
            out.write('{0}\n'.format(value))

def convertmod2vtk(out_file, inp_file, ohm_file=None):
    # only use topography if ohm file is given
    topography = ohm_file is not None

    x_coordinate_pair, z_coordinate_pair, rho, coverage = read_mod_file(inp_file)

    if topography:
        topo = read_ohm_file(ohm_file)

    # create list of grid cells from grid points
    points, cells = create_geometry(x_coordinate_pair, z_coordinate_pair)

    if topography:
        for point in points:
            if point.x in topo:
                point.z += topo[point.x]
            else:
                # use nearest topography point
                point.z += topo[min(topo.keys(), key=lambda k: abs(k-point.x))]

    # convert relative coordinates to UTM
    startpoint = Point3D(356933, 5686395, 0)
    endpoint = Point3D(357127, 5686380, 0)
    for point in points:
        point.x, point.y, _ = convert_relative_to_utm(startpoint, endpoint, point.x)

    write_vtk_file(out_file, os.path.split(inp_file)[1], points, cells, rho, coverage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Converts .mod to .vtk file")
    parser.add_argument("output_vtk", help="Filename of .vtk file in which the results are saved.")
    parser.add_argument("input_mod", help="Filename of .mod file from which inputs are read.")
    parser.add_argument("input_ohm", nargs="?", default=None, help="Filename of .ohm file from which inputs are read. Optional, only used for topography.")
    args = parser.parse_args()

    convertmod2vtk(args.output_vtk, args.input_mod, args.input_ohm)

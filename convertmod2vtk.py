#!/usr/bin/env python3

import argparse
import itertools
import os
from math import atan2, cos, sin

from src.io.read import read_mod_file, topography_from_dem, topography_from_ohm
from src.utils import get_file_ending
from src.point import Point3D
from src.io.write import write_vtk_file


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
    # TODO benutze Geradengleichung
    connecting_vector = endpoint - startpoint
    angle_radians = atan2(connecting_vector.y, connecting_vector.x)
    dx = cos(angle_radians) * relative_distance
    dy = sin(angle_radians) * relative_distance
    return Point3D(startpoint.x + dx, startpoint.y + dy, startpoint.z)


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
    points = []  # list of all unique points read from vtk file
    cells = []  # list of lists, every sublists contains indices of points of a cell in points list
    for x_pair, z_pair in zip(x_coordinate_pair, z_coordinate_pair):
        cell = []  # list that holds the index of corner points of the cell
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


def convertmod2vtk(out_file, inp_file, start_point, end_point, topo_file=None):
    """

    :param out_file:
    :type out_file:
    :param inp_file:
    :type inp_file:
    :param topo_file: File from which topography should be read. Either a .tif
    containing a dem model or an ohm file with topography
    :type topo_file: str
    :param dem_file:
    :type dem_file:
    :return:
    :rtype:
    """
    x_coordinate_pair, z_coordinate_pair, rho, coverage = read_mod_file(inp_file)

    # create list of grid cells from grid points
    points, cells = create_geometry(x_coordinate_pair, z_coordinate_pair)

    # read elevation from dem model or ohm file and set points z coordinate
    if topo_file is not None:
        if get_file_ending(topo_file) == "tif":
            # tif file needs coordinates in utm, convert first
            # convert relative coordinates to UTM
            start_point.append(0.0)
            end_point.append(0.0)
            startpoint = Point3D(*start_point)
            endpoint = Point3D(*end_point)
            for point in points:
                point.x, point.y, _ = convert_relative_to_utm(startpoint, endpoint, point.x)
                # update elevation
            points = topography_from_dem(topo_file, points)
        elif get_file_ending(topo_file) == "ohm":
            # ohm file has elevation in relative coordinates, read topography first, then convert to UTM
            points = topography_from_ohm(topo_file, points)
            # convert relative coordinates to UTM
            start_point.append(0.0)
            end_point.append(0.0)
            startpoint = Point3D(*start_point)
            endpoint = Point3D(*end_point)
            for point in points:
                point.x, point.y, _ = convert_relative_to_utm(startpoint, endpoint, point.x)
        else:
            raise Exception("Wrong topography file given!")

    write_vtk_file(out_file, os.path.split(inp_file)[1], points, cells, rho, coverage)


def main():
    parser = argparse.ArgumentParser(description="Converts .mod to .vtk file, adding surface geometry.")
    parser.add_argument("output_vtk", help="Filepath/filename of .vtk file in which the results are saved.")
    parser.add_argument("input_mod", help="Filepath/filename of .mod file from which inputs are read.")
    parser.add_argument("input_topo", help="Filepath/filename of dem model or ohm file used for elevation")
    parser.add_argument("start_point", nargs=2, type=float, help="UTM north east coordinate of start point")
    parser.add_argument("end_point", nargs=2, type=float, help="UTM north east coordinate of end point")
    args = parser.parse_args()

    convertmod2vtk(args.output_vtk, args.input_mod, args.start_point, args.end_point, args.input_topo)

if __name__ == '__main__':
    main()

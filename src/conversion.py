import itertools
import os
from math import atan2, cos, sin
from geoelectricalSurveyTools.src.io.read import read_mod_file
from geoelectricalSurveyTools.src.io.write import write_vtk_file
from geoelectricalSurveyTools.src.utils import get_file_ending
from geoelectricalSurveyTools.src.point import Point3D
from geoelectricalSurveyTools.src.geometry import topography_from_dem, topography_from_ohm, create_geometry


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


def convertmod2vtk(out_file, inp_file, start_point, end_point, topo_file=None):
    """

    :param out_file: Filepath/filename of vtk file to write
    :type out_file: str
    :param inp_file: Filename/filepath of .mod file from which data is read
    :type inp_file: str
    :param end_point: coordinates of end point in UTM
    :type end_point: list of two values, x and y/north and east coordinate
    :param start_point: coordinates of start point in UTM
    :type start_point: list of two values, x and y/north and east coordinate
    :param topo_file: File from which topography should be read. Either a .tif
    containing a dem model or an ohm file with topography
    :type topo_file: str
    """
    x_coordinate_pair, z_coordinate_pair, rho, coverage = read_mod_file(inp_file)

    # create list of grid cells from grid points
    points, cells = create_geometry(x_coordinate_pair, z_coordinate_pair)

    # convert coordinates from list to Point3D object
    if start_point is None or end_point is None:
        start_point = [x_coordinate_pair[0][1], 0.]
        end_point = [x_coordinate_pair[-1][0], 0.]
    # set height zo zero
    start_point.append(0.0)
    end_point.append(0.0)
    startpoint = Point3D(*start_point)
    endpoint = Point3D(*end_point)

    # read elevation from dem model or ohm file and set points z coordinate
    if topo_file is not None:
        if get_file_ending(topo_file) == "tif":
            # tif file needs coordinates in utm, convert first
            # convert relative coordinates to UTM
            for point in points:
                point.x, point.y, _ = convert_relative_to_utm(startpoint, endpoint, point.x)
                # update elevation
            points = topography_from_dem(topo_file, points)
        elif get_file_ending(topo_file) == "ohm":
            # ohm file has elevation in relative coordinates, read topography first, then convert to UTM
            points = topography_from_ohm(topo_file, points)
            # convert relative coordinates to UTM
            for point in points:
                point.x, point.y, _ = convert_relative_to_utm(startpoint, endpoint, point.x)
        else:
            raise Exception("Wrong topography file given!")

    write_vtk_file(out_file, os.path.split(inp_file)[1], points, cells, rho, coverage)
import itertools
from geoelectricalSurveyTools.src.point import Point3D
from geoelectricalSurveyTools.src.DigitalElevationModel import DEM
from geoelectricalSurveyTools.src.utils import distance
from geoelectricalSurveyTools.src.io.read import read_ohm_file


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


def topography_from_dem(dem_file, points):
    """Read elevation from model and modify z coordinate of every point"""
    dem_model = DEM(dem_file)
    electrode_distance = distance(points[0], points[1])
    for point in points:
        point.z = dem_model.get_height((point.x, point.y),
                                       electrode_distance / 2)
    return points


def topography_from_ohm(ohm_file, points):
    topo = read_ohm_file(ohm_file)
    for point in points:
        if point.x in topo:
            point.z += topo[point.x]
        else:
            # use nearest topography point
            point.z += topo[
                min(topo.keys(), key=lambda k: abs(k - point.x))]
    return points
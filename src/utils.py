"Small utility functions"

from math import hypot


def get_file_ending(filepath):
    return filepath.split(".")[-1]


def distance(point1, point2):
    """
    Return distance between point1 and point2 in xy plane
    :type point1: Point3D
    :type point2: Point3D
    :rtype: float
    """
    connecting_vector = point1 - point2
    return hypot(connecting_vector.x, connecting_vector.y)
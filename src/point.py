"""Point class for 3D points"""


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

    def get_horizontal_coordinate_pair(self):
        """
        Return horizontal coordinate pair as a list for functions that dont work with Point3D classes
        :return: [x, y] coordinate
        :rtype: list
        """
        return [self.x, self.y]

    def __iter__(self):
        # make class iterable by returning x, then y then z coordinate
        return iter((self.x, self.y, self.z))

    def __eq__(self, other):
        # Compare two points, return true if they have the same coordinates
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __sub__(self, other):
        # Subtraction of two points by subtracting all coordinates
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __repr__(self):
        return "Point3D({x}, {y}, {z})".format(x=self.x, y=self.y, z=self.z)
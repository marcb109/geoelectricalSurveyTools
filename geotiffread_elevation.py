import gdal
import numpy as np
from operator import itemgetter
from scipy import spatial

class DEM_Model:

    def __init__(self, filepath):
        """
        Open the digital elevation model given at filepath, read the coordinates and build a KDTree of coordinate/height
        :param filepath:
        """
        dataset = gdal.Open(filepath)
        self._coord_ele_data = []
        dataset_band = dataset.GetRasterBand(1)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        #print(rows, cols)
        data = dataset_band.ReadAsArray(0, 0, cols, rows)
        transform = dataset.GetGeoTransform()
        xOrigin_upperleft = transform[0]
        yOrigin_upperleft = transform[3]
        pixelXWidth = transform[1]
        pixelYWidth = transform[2]
        pixelXHeight = transform[4]
        pixelYHeight = transform[5]
        for i in range(0, cols):
            for j in range(0, rows):
                x_coord = xOrigin_upperleft + pixelXWidth * i + pixelYWidth * j
                y_coord = yOrigin_upperleft + pixelXHeight * i + pixelYHeight * j
                elevation = data[j][i]
                self._coord_ele_data.append((x_coord, y_coord, elevation))

        self._coord_ele_data.sort(key=itemgetter(0))
        self._coord_ele_data.sort(key=itemgetter(1))
        coord_data = [(coord[0], coord[1]) for coord in self._coord_ele_data]
        self._kdtree = spatial.cKDTree(coord_data)  # create kd-Tree of coordinate data to speed up the search for coordinates

    def get_height(self, utm_coordinate, interpolation_distance):
        """
        Find coordinates falling into each element of the box, take the average of the elevation of the coordinates
        in one element and assign averaged elevation to that element
        :param utm_coordinate: tuple of utm coordinates (north, east)
        :param interpolation_distance: distance around given coordinate in m to look for points
        :return: average elevation of points around the given coordinate
        """
        indices = self._kdtree.query_ball_point(utm_coordinate, interpolation_distance)
        close_points = [self._coord_ele_data[index] for index in indices]
        elevations = [point[2] for point in close_points]
        return np.average(elevations)


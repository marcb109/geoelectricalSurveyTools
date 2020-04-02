"""Functions for writing data to files"""


def write_vtk_file(vtk_filename, input_filename, points, cells, rho, coverage):
    num_points = len(points)
    num_cells = len(cells)
    # write VTK file
    with open(vtk_filename, 'w', newline='\n') as out:
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


def write_vtk_file_general(vtk_filename, title, points, cells, values, value_descriptors):
    """
    General method to write an unstructured grid to a vtk file
    :param vtk_filename: Filename with which to save .vtk file
    :type vtk_filename: str
    :param title: Title of vtk file, 256 characters maximum
    :param points: list of points to save in vtk file
    :type points: list
    :param cells: list of cells to save in vtk file. A cell is defined by the indices of its
    four vertices in the list of points
    :type cells: list
    :param values: list of lists of data. All lists will be save as their own data set
    :type values: list
    :param value_descriptors: list of data descriptors accompanying values such as 'rho float'.
    Can be used to identify data sets in paraview.
    :type value_descriptors: list of strings
    :rtype: None
    """
    num_points = len(points)
    num_cells = len(cells)
    # write VTK file
    with open(vtk_filename, 'w', newline='\n') as out:
        # write header
        out.write('# vtk DataFile Version 3.0\n')
        out.write(title + '\n')
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
        for value_set, value_set_description in zip(values, value_descriptors):

            out.write('SCALARS {} 1\n'.format(value_set_description))
            out.write('LOOKUP_TABLE default\n')
            for value in value_set:
                out.write('{0}\n'.format(value))

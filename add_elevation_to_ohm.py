import argparse
from geotiffread_elevation import DEM_Model
from convertmod2vtk import convert_relative_to_utm, Point3D

def create_model(dem_file):
    print("Creating DEM Model")
    dem_model = DEM_Model(dem_file)
    print("DEM Model creation finished")
    return dem_model

def append_height_to_ohm(ohm_file, dem_model, start, end):
    with open(ohm_file, 'r') as ohm:
        lines = ohm.readlines()
    num_electrodes = int(lines[0].split('#')[0])
    index_firstline = lines.index('# x z\n') + 1
    index_lastline = index_firstline + num_electrodes
    values = lines[index_firstline:index_lastline]
    values = [[float(val) for val in value.split()] for value in values]


    # search for old top values in file and delete them
    try:
        index = lines.index('# x h for each topo point\n')
        # file contains old values, delete them
        lines = lines[:index-1]
    except ValueError:
        # no old values found in file
        pass

    # convert relative coordinates to utm
    start = Point3D(*start, z=0)
    end = Point3D(*end, z=0)
    electrode_distance = abs(values[0][0] - values[1][0])
    print("Getting elevation from DEM model")
    for value in values:
        utm_point = convert_relative_to_utm(start, end, value[0])
        value[1] = dem_model.get_height((utm_point.x, utm_point.y), electrode_distance/2)

    print("Writing output ohm file")
    with open(ohm_file, 'w') as ohm:
        # write old data
        for line in lines:
            ohm.write(line)
        # append header to ohm file
        ohm.write('{} # Number of topo points\n'.format(num_electrodes))
        ohm.write('# x h for each topo point\n')
        # append converted values to ohm file
        for value_pair in values:
            ohm.write('{}\t{}\n'.format(*value_pair))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_ohm', help='Ohm file for which the elevation should be appended')
    parser.add_argument('dem_file', help='DEM file to read for elevation data')
    parser.add_argument('--start', nargs=2, type=float, help='north east coordinate of start point in utm')
    parser.add_argument('--end', nargs=2, type=float, help='north east coordinate of end point in utm')
    args = parser.parse_args()
    print(args)
    append_height_to_ohm(args.input_ohm, args.dem_file, args.start, args.end)
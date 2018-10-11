"""Functions for reading data from files"""

from geoelectricalSurveyTools.src.DigitalElevationModel import DEM
from geoelectricalSurveyTools.src.utils import distance


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
    index = lines.index('# x h for each topo point\n')
    lines = lines[index + 1:]
    # num_topopoints = int(lines[index-1].split('#')[0])
    # convert list of strings to list of lists of float
    lines = [[float(number) for number in line.split()] for line in lines]
    x_topo = [line[0] for line in lines]
    z_topo = [line[1] for line in lines]
    topo = dict(zip(x_topo, z_topo))
    return topo

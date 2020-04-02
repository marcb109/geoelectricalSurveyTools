#!/usr/bin/env python3

import argparse
import sys
from src.conversion import convertmod2vtk


def main():
    epilog_string = """\
    Example calls: 
	convertmod2vtk.py Profil1.vtk Profil1.mod
        Just read data from Profil1.mod and save it in Profil1.vtk file. No topography is added. Relative coordinates are kept.

    convertmod2vtk.py Profil1.vtk Profil1.mod -s 378455 5701392 -e 378455 5701392 -t Profil1.ohm
        This would call the script to read topography from the ohm file and use a 
        start point of 378455 5701392 and an end point of 378455 5701392. Output is 
        saved to the Profil1.vtk file.

    convertmod2vtk.py Profil1_Topo.vtk Profil1.mod -s 378455 5701392 -e 378455 5701392 -t model/DEM.tif
        Same as above, but topography is read from Tif file containing a Digital Elevation Model"""

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="Converts .mod to .vtk file, adding surface geometry.",
                                     epilog=epilog_string)
    parser.add_argument("output_vtk", help="Filepath/filename of .vtk file in which the results are saved.")
    parser.add_argument("input_mod", help="Filepath/filename of .mod file from which inputs are read.")
    parser.add_argument("-t", "--input_topo", nargs='?', help="Filepath/filename of dem model or ohm file used for elevation")
    parser.add_argument("-s", "--start_point", nargs=2, type=float, help="UTM north east coordinate of start point of array. If no start and end point is given, the relative coordinates from the .mod file will be kept.")
    parser.add_argument("-e", "--end_point", nargs=2, type=float, help="UTM north east coordinate of end point of array")
    if len(sys.argv) < 2:
        # if no options were used, print help.
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args()
        convertmod2vtk(args.output_vtk, args.input_mod, args.start_point, args.end_point, args.input_topo)


if __name__ == '__main__':
    main()

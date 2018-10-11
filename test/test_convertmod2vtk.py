import os
import unittest
import filecmp
from convertmod2vtk import convertmod2vtk


class TestWholeScript(unittest.TestCase):

    """Simple Test that looks if the .vtk file stays the same as a known good version. Used for regression testing
    during development, not a sanity check of the result."""

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.input_file_mod = os.path.join(dir_path, "Profil1.mod")
        self.topo_file = os.path.join(dir_path, "Profil1.ohm")
        self.output_file_name = os.path.join(dir_path, "Profil1_Result.vtk")
        self.output_file_correct_result = os.path.join(dir_path, "Profil1_Richtiges_Ergebnis.vtk")

    def test_convertmod2vtk(self):
        # remove old results if they exist
        try:
            os.remove(self.output_file_name)
        except FileNotFoundError: pass
        start = [356933, 5686395]
        end = [357127, 5686380]
        convertmod2vtk(self.output_file_name, self.input_file_mod, start, end, self.topo_file)
        self.assertTrue(filecmp.cmp(self.output_file_correct_result, self.output_file_name), msg='Result of convertmod2vtk is different different from expected result!')

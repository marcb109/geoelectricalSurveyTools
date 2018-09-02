import os
import unittest
from convertmod2vtk import convertmod2vtk
import filecmp


class TestWholeScript(unittest.TestCase):

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.input_file_mod = os.path.join(dir_path, "Profil1.mod")
        self.output_file_name = os.path.join(dir_path, "Profil1_Result.vtk")
        self.output_file_correct_result = os.path.join(dir_path, "Profil1_Richtiges_Ergebnis.vtk")
        print(self.output_file_correct_result)

    def test_convertmod2vtk(self):
        # remove old results if they exist
        try:
            os.remove(self.output_file_name)
        except FileNotFoundError: pass
        convertmod2vtk(self.output_file_name, self.input_file_mod)
        self.assertTrue(filecmp.cmp(self.output_file_correct_result, self.output_file_name), msg='Result of convertmod2vtk is different different from expected result!')

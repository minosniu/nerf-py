'''
Created on Aug 29, 2012

@author: labuser
'''
import unittest
from core import Waveclass


class Test(unittest.TestCase):

    def testSeq(self):
        waveclass = Waveclass(category = "SeqGenerator")

    def testSine(self):
        dut = Waveclass(category = "SineGenerator")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
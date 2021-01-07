import unittest
from selenium import webdriver

class SampleTest(unittest.TestCase):
    """A class to do a few small, simple tests as a trial run for selenium and
       unittest."""

    def test_first(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
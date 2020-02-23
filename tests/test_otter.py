import unittest
import otter

class TestApp(unittest.TestCase):

    def setUp(self):
        pass

    def test_version(self):
        self.assertEqual(otter.VERSION, 1.0)

    def test_copyright(self):
        self.assertEqual(otter.COPYRIGHT, u"Copyright © 2020, David Andrš, All Rights Reserved")


if __name__ == '__main__':
    unittest.main()

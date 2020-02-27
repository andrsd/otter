import unittest
from otter import common

class TestApp(unittest.TestCase):

    def test_viewport(self):
        ipol = common.LinearInterpolation([0, 1], [1, 2])
        self.assertEqual(ipol(-1), 1.0)
        self.assertEqual(ipol(0.5), 1.5)
        self.assertEqual(ipol(2), 2)

if __name__ == '__main__':
    unittest.main()

import os
import unittest


class TestConfig(unittest.TestCase):
    pathToThisScriptFile = os.path.dirname(os.path.realpath(__file__))
    valid = os.path.join(pathToThisScriptFile, "fixtures/config.py")
    invalid = os.path.join(pathToThisScriptFile, "fixtures/config_invalid.py")

    def test_valid(self):
        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.main()

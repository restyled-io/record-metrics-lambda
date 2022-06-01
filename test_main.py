import unittest
import warnings

import main


class TestMain(unittest.TestCase):
    def setUp(self):
        # https://github.com/boto/boto3/issues/454
        warnings.filterwarnings("ignore",
                                category=ResourceWarning,
                                message="unclosed.*<ssl.SSLSocket.*>")
        warnings.filterwarnings("ignore",
                                category=DeprecationWarning,
                                message="ssl.*")

    def test_handler(self):
        result = main.handler(None, None)
        self.assertEqual(result['ok'], True)
        self.assertEqual(result['env'], 'prod')


if __name__ == '__main__':
    unittest.main()

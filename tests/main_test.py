import boto3
import mock
import unittest


import os.path

from functions.convert.main import handle

class MainTest(unittest.TestCase):

    mock_upload_file = mock.MagicMock()

    @staticmethod
    def mock_client(*args):
        result = mock.Mock()
        result.upload_file = MainTest.mock_upload_file
        return result

    def test_empty(self):
        boto3.client = MainTest.mock_client

        here = os.path.abspath(os.path.dirname(__file__))
        cdn_bucket = "bucket"
        cdn_file = "file"
        event = {
            "job" : {
                "source" : "file:{}".format(os.path.join(here, "resources/test.zip"))
            },
            "upload" : {
                "cdn_bucket" : cdn_bucket,
                "cdn_file" : cdn_file
            }
        }
        handle(event, context=None)
        args, kwargs = MainTest.mock_upload_file.call_args
        self.assertEqual(len(args), 3)
        self.assertEqual(len(kwargs), 0)
        self.assertEqual(args[1], cdn_bucket)
        self.assertEqual(args[2], cdn_file)
        result = args[0]
        self.assertTrue(os.path.isfile(result))

if __name__ == "__main__":
    unittest.main(verbosity=3)

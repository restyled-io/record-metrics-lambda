import unittest

import main

TEST_ENV = "prod"
TEST_QUEUE = "restyled:agent:webhooks"
TEST_PARAM = "/restyled/{}/redis-url".format(TEST_ENV)
TEST_REDIS_URL = "http://redis.restyled.com:6379/1"


class TestMain(unittest.TestCase):
    """ """

    def test_handler(self):
        """ """
        aws = MockAWS()
        aws.ssm_parameters[TEST_PARAM] = TEST_REDIS_URL
        redis = MockRedis()
        redis.llens[TEST_QUEUE] = 3
        logger = main.get_logger("ERROR")
        expected_metric = {
            "Dimensions": [
                {
                    "Name": "Environment",
                    "Value": TEST_ENV
                },
                {
                    "Name": "QueueName",
                    "Value": TEST_QUEUE
                },
            ],
            "MetricName":
            "QueueDepth",
            "Unit":
            "Count",
            "Value":
            3,
        }
        expected_metrics = [{
            "MetricData": [expected_metric],
            "Namespace": "Restyled",
        }]

        result = main.handler_(aws, redis, TEST_ENV, TEST_QUEUE, logger)

        self.assertEqual(aws.cloudwatch_metrics, expected_metrics)


class MockAWS:
    """ """

    def __init__(self):
        self.ssm_parameters = {}
        self.cloudwatch_metrics = []

    def ssm_get_parameter(self, *args, **kwargs):
        """

        :param *args:
        :param **kwargs:

        """
        name = kwargs.get("Name")
        value = self.ssm_parameters[name]

        return {"Parameter": {"Value": value}}

    def cloudwatch_put_metric_data(self, *args, **kwargs):
        """

        :param *args:
        :param **kwargs:

        """
        self.cloudwatch_metrics.append(kwargs)


class MockRedis:
    """ """

    def __init__(self):
        self.llens = {}

    def setup(self, *args, **kwargs):
        """

        :param *args:
        :param **kwargs:

        """
        pass

    def llen(self, queue):
        """

        :param queue:

        """
        return self.llens[queue]


if __name__ == "__main__":
    unittest.main()

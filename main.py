import json
import logging
import os
import sys

import boto3
import redis
import requests
import structlog


def extend_event(_logger, log_method, event_dict):
    event_dict['level'] = log_method
    event_dict['message'] = event_dict['event']
    event_dict.pop('event')

    return event_dict


logging.basicConfig(format="%(message)s",
                    stream=sys.stdout,
                    level=logging.INFO)

structlog.configure(
    processors=[extend_event,
                structlog.processors.JSONRenderer()],
    logger_factory=structlog.stdlib.LoggerFactory(),
)


def handler(_event, _context):
    try:
        # TODO: record for any deployed environments/queues
        env = os.environ.get('ENV', 'prod')
        queue = os.environ.get('QUEUE', 'restyled:agent:webhooks')

        logger = structlog.get_logger("record-metrics")
        logger.info("Recording metrics", env=env, queue=queue)

        dimensions = [{
            'Name': 'Environment',
            'Value': env
        }, {
            'Name': 'QueueName',
            'Value': queue
        }]

        url = get_redis_url(env)
        r = redis.Redis.from_url(url)
        depth = r.llen(queue)

        cw = boto3.client('cloudwatch')
        cw.put_metric_data(Namespace='Restyled',
                           MetricData=[{
                               'MetricName': 'QueueDepth',
                               'Value': depth,
                               'Unit': 'Count',
                               'Dimensions': dimensions
                           }])

        return {'ok': True, 'env': env, 'queue': queue, 'depth': depth}
    except Exception as ex:
        logger.error("Exception", exception=ex)

        return {'ok': False, 'env': env, 'queue': queue}


def get_redis_url(env):
    ssm = boto3.client('ssm')
    token_parameter_name = "/restyled/%s/redis-url" % env
    token_parameter = ssm.get_parameter(Name=token_parameter_name)

    return token_parameter['Parameter']['Value']


if __name__ == '__main__':
    result = handler(None, None)
    print(json.dumps(result, indent=2))

import json
import os

import boto3
import redis
import requests


def handler(_event, _context):
    # TODO: record for any deployed environments/queues
    env = os.environ.get('ENV', 'prod')
    queue = os.environ.get('QUEUE', 'restyled:agent:webhooks')
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


def get_redis_url(env):
    ssm = boto3.client('ssm')
    token_parameter_name = "/restyled/%s/redis-url" % env
    token_parameter = ssm.get_parameter(Name=token_parameter_name)

    return token_parameter['Parameter']['Value']


if __name__ == '__main__':
    result = handler(None, None)
    print(json.dumps(result, indent=2))

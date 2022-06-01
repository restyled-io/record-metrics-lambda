import json
import logging
import os
import sys

import boto3
import redis
import requests
import structlog


def copy_event_to_message(_logger, _log_method, event_dict):
    event_dict['message'] = event_dict['event']

    return event_dict


def get_logger(log_level_str):
    processors = [
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(),
        structlog.processors.CallsiteParameterAdder(), copy_event_to_message,
        structlog.processors.JSONRenderer()
    ]

    log_level = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }.get(log_level_str.lower())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level))

    return structlog.get_logger()


def handler(_event, _context):
    env = os.environ.get('ENV', 'prod')
    queue = os.environ.get('QUEUE', 'restyled:agent:webhooks')
    log_level = os.environ.get('LOG_LEVEL', 'info')
    logger = get_logger(log_level)
    dimensions = [{
        'Name': 'Environment',
        'Value': env
    }, {
        'Name': 'QueueName',
        'Value': queue
    }]

    try:
        url = get_redis_url(env)
        r = redis.Redis.from_url(url)
        depth = r.llen(queue)

        logger.info('Putting depth metric',
                    app='record-metrics',
                    env=env,
                    queue=queue,
                    depth=depth)

        cw = boto3.client('cloudwatch')
        cw.put_metric_data(Namespace='Restyled',
                           MetricData=[{
                               'MetricName': 'QueueDepth',
                               'Value': depth,
                               'Unit': 'Count',
                               'Dimensions': dimensions
                           }])

        return {'ok': True, 'env': env, 'queue': queue, 'depth': depth}
    except:
        logger.error("Exception", exc_info=True)

        return {'ok': False, 'env': env, 'queue': queue}


def get_redis_url(env):
    ssm = boto3.client('ssm')
    token_parameter_name = "/restyled/%s/redis-url" % env
    token_parameter = ssm.get_parameter(Name=token_parameter_name)

    return token_parameter['Parameter']['Value']


if __name__ == '__main__':
    result = handler(None, None)
    print(json.dumps(result, indent=2))

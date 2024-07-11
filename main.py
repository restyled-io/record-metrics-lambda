import json
import logging
import os
from urllib.parse import urlparse

import boto3
import requests
import structlog
from redis import Redis as RealRedis


class AWS:

    def ssm_get_parameter(self, *args, **kwargs):
        ssm = boto3.client("ssm")

        return ssm.get_parameter(*args, **kwargs)

    def cloudwatch_put_metric_data(self, *args, **kwargs):
        cw = boto3.client("cloudwatch")

        return cw.put_metric_data(*args, **kwargs)


class Redis:

    def setup(self, *args, **kwargs):
        if self.redis is None:
            self.redis = RealRedis(*args, **kwargs)

        return self

    def llen(self, queue):
        return self.redis.llen(queue)


def copy_event_to_message(_logger, _log_method, event_dict):
    event_dict["message"] = event_dict["event"]

    return event_dict


def get_logger(log_level_str):
    processors = [
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(),
        structlog.processors.CallsiteParameterAdder(),
        copy_event_to_message,
        structlog.processors.JSONRenderer(),
    ]

    log_level = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }.get(log_level_str.lower())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )

    return structlog.get_logger()


def handler(event, context):
    env = os.environ.get("ENV", "prod")
    queue = os.environ.get("QUEUE", "restyled:agent:webhooks")
    log_level = os.environ.get("LOG_LEVEL", "info")
    logger = get_logger(log_level)

    aws = AWS()
    redis = Redis()

    try:
        return handler_(aws, redis, env, queue, logger)
    except:
        logger.error("Exception", exc_info=True)

        return {"ok": False, "env": env, "queue": queue}


def handler_(aws, redis, env, queue, logger):
    dimensions = [
        {
            "Name": "Environment",
            "Value": env
        },
        {
            "Name": "QueueName",
            "Value": queue
        },
    ]

    url = get_redis_url(aws, env)

    if url.scheme == "rediss":
        redis.setup(
            host=url.hostname,
            port=url.port,
            password=url.password,
            ssl=True,
            ssl_cert_reqs=None,
        )
    else:
        redis.setup(host=url.hostname, port=url.port, password=url.password)

    depth = redis.llen(queue)

    logger.info(
        "Putting depth metric",
        app="record-metrics",
        env=env,
        queue=queue,
        depth=depth,
    )

    aws.cloudwatch_put_metric_data(
        Namespace="Restyled",
        MetricData=[{
            "MetricName": "QueueDepth",
            "Value": depth,
            "Unit": "Count",
            "Dimensions": dimensions,
        }],
    )

    return {"ok": True, "env": env, "queue": queue, "depth": depth}


def get_redis_url(aws, env):
    token_parameter_name = "/restyled/%s/redis-url" % env
    token_parameter = aws.ssm_get_parameter(Name=token_parameter_name)

    return urlparse(token_parameter["Parameter"]["Value"])


if __name__ == "__main__":
    result = handler(None, None)
    print(json.dumps(result, indent=2))

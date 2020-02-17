#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# bug-report: makssych@gmail.com

""" grafana/loki exporter get data from loki """

import logging
import logging.handlers
import os
import requests
import sys
from prometheus_client import Gauge


logger = logging.getLogger(os.path.splitext(os.path.basename(sys.argv[0]))[0])

pr_metrics = {}

def loki_get(query, loki_host, metrics={}):
    logger.debug("query={}".format(query["q"]))

    url = '{}/loki/api/v1/query'.format(loki_host)
    params = {
    "query": "{}".format(query["q"])
    }
    
    resp = requests.get(url, params=params)
    logger.debug("request status code: {}".format(resp.status_code))
    if resp.status_code == 200 and resp.json()["data"]["result"] != []:
        resp_data = resp.json()
        logger.debug(resp_data["data"]["result"])
        try:
            print(pr_metrics[query["name"]])
        except(KeyError):
            pr_metrics[query["name"]] = Gauge(query["name"], query.get("descrition", 'No description of gauge'))
        # Set to a given value
        logger.info("Set Gauge for metric name {}: {}".format(
            query["name"],
            resp_data["data"]["result"][0]["value"][1])
            )
        pr_metrics[query["name"]].set(float(resp_data["data"]["result"][0]["value"][1]))

# c = Counter('my_requests_total', 'HTTP Failures', ['method', 'endpoint'])
# c.labels(method='get', endpoint='/').inc()
# c.labels(method='post', endpoint='/submit').inc()

def create_metrics(file_options):
    for query in file_options["queris"]:
        loki_get(query, file_options["loki_host"], file_options["metrics"])


if __name__ == '__main__':
    pass
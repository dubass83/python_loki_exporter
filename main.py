#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# bug-report: makssych@gmail.com

""" grafana/loki exporter main file """

import logging
import logging.handlers
import os
import argparse
import sys
import json
import atexit
from datetime import datetime, date, timedelta
from loki_get import create_metrics
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from prometheus_client import make_wsgi_app
from apscheduler.schedulers.background import BackgroundScheduler

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter,):
    pass

parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__,
                                 formatter_class=CustomFormatter,)
logger = logging.getLogger(os.path.splitext(os.path.basename(sys.argv[0]))[0])


def setup_logging(options):
    """Configure logging."""
    root = logging.getLogger('')
    root.setLevel(logging.WARNING)
    logger.setLevel(options.debug and logging.DEBUG or logging.INFO)
    if not options.silent:
        ch = logging.StreamHandler()
        ch.setFormatter(
            logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            ),
        )
        root.addHandler(ch)


def parse_args(args=sys.argv[1:]):
    """Parse arguments."""
    # Config file
    g = parser.add_argument_group('config file')
    g.add_argument(
        '--file', '-f',
        required=True,
        type=str,
        help='set path to config file',
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        '--debug', '-d', action='store_true',
        default=True,
        help='enable debugging',
    )
    g.add_argument(
        '--silent', '-s', action='store_true',
        default=False,
        help="don't log to console",
    )

    return parser.parse_args(args)

def get_options():
    """ main entrance """
    # try get options 
    try:
        options = parse_args()
        setup_logging(options)
    except:
        parser.print_help()
        sys.exit(0)
    # try read config from file
    try:
        with open('{}'.format(options.file)) as json_data_file:
            file_options = json.load(json_data_file)
    except FileNotFoundError:
        logger.error(f"No such file or directory: {options.file}")
        logger.error("Try get options from comand line")
        parser.print_help()
        sys.exit(0)
    return file_options

options = get_options()

def run(file_options=options):
    logger.info("#============  Started ==============#")
    logger.debug(file_options)
    create_metrics(file_options)
    logger.info("#============  Finshed ==============#")

# Create my app
app = Flask(__name__)

scheduler = BackgroundScheduler()
scheduler.add_job(func=run, trigger="interval", seconds=options.get("timeout", 10))
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Add prometheus wsgi middleware to route /metrics requests
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})


if __name__ == '__main__':
    run_simple(hostname="localhost", port=options.get("server_port", 8080), application=app_dispatch)


        
#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import requests
import logging
import time


logger = logging.getLogger('data')


default_requests_session = requests.Session()
default_requests_session.headers['User-Agent'] =\
    "Andrew Head (for academic research) <andrewhead@eecs.berekeley.edu>"


def make_request(method, *args, **kwargs):

    # We read the max_attempts and retry_delay arguments from the kwargs dictionary
    # instead of named kwargs because we want to preserve the order of the
    # "request" method's positional arguments for clients of this method.
    max_attempts = kwargs.get('max_attempts', 2)
    retry_delay = kwargs.get('retry_delay', 10)

    try_again = True
    attempts = 0
    res = None

    def log_error(err_msg):
        logger.warn(
            "Error (%s) For API call %s, Args: %s, Kwargs: %s",
            str(err_msg), str(method), str(args), str(kwargs)
        )

    while try_again and attempts < max_attempts:

        try:
            res = method(*args, **kwargs)
            if hasattr(res, 'status_code') and res.status_code not in [200]:
                log_error(str(res.status_code))
                res = None
            try_again = False
        except requests.exceptions.ConnectionError:
            log_error("ConnectionError")
        except requests.exceptions.ReadTimeout:
            log_error("ReadTimeout")

        if try_again:
            logger.warn("Waiting %d seconds for before retrying.", int(retry_delay))
            time.sleep(retry_delay)
            attempts += 1

    return res

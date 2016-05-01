#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from peewee import fn
import time
import json

from fetch.api import make_request, default_requests_session
from models import Publication
from lock import lock_method


logger = logging.getLogger('data')


# Query URL and parameters from http://stackoverflow.com/questions/5102878/google-suggest-api
URL = "https://api.projectoxford.ai/academic/v1.0/evaluate"
DEFAULT_PARAMS = {
    'attributes': "Ti,CC,Y,AA.AuN",
}
REQUEST_DELAY = 1.5
LOCK_FILENAME = '/tmp/citation-count-fetcher.lock'


def get_citation_count_for_queries(queries, api_key):

    # Create a new fetch index.
    last_fetch_index = Publication.select(
        fn.Max(Publication.fetch_index)).scalar() or 0
    fetch_index = last_fetch_index + 1

    for query in queries:

        # Fetch the citation count!
        get_citation_count(query, fetch_index, api_key)


def get_citation_count(query, fetch_index, api_key):

    # Request for citation counts for the publication
    params = DEFAULT_PARAMS.copy()
    params['expr'] = (
        "AND(" +  # we will search based on two criteria:
        "Ti=\'{title}\'...," +  # the title prefix
        "Y={year})"  # the publication year
        ).format(title=query['title'], year=int(query['year']))
    response = make_request(
        default_requests_session.get,
        URL,
        params=params,
        headers={'Ocp-Apim-Subscription-Key': api_key},
    )
    time.sleep(REQUEST_DELAY)  # enforce a pause between each fetch to be respectful to API

    # Go no further if the call failed
    if not response:
        return

    publications = response.json()['entities']
    if len(publications) == 0:
        logger.warn("No publications found for title: %s", query['title'])
        return

    # Store data from the fetched publications
    first_publication = publications[0]
    authors = ','.join([author['AuN'] for author in first_publication['AA']])
    Publication.create(
        fetch_index=fetch_index,
        citation_count=first_publication['CC'],
        author=authors,
        year=first_publication['Y'],
        title=first_publication['Ti'],
    )


@lock_method(LOCK_FILENAME)
def main(queries, microsoft_credentials, *args, **kwargs):

    with open(microsoft_credentials) as credentials_file:
        credentials = json.load(credentials_file)
        api_key = credentials['apiKey']

    with open(queries) as queries_file:
        query_list = json.load(queries_file)
        get_citation_count_for_queries(query_list, api_key)


def configure_parser(parser):
    parser.description = "Fetch citation counts for publications."
    parser.add_argument(
        'queries',
        type=str,
        help="the name of a JSON file containing a list of specification for publication queries."
    )
    parser.add_argument(
        'microsoft_credentials',
        type=str,
        help="the name of a JSON file containing a Microsoft Academic API key."
    )

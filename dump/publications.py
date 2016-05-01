#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging

from dump import dump_csv
from models import Publication


logger = logging.getLogger('data')


@dump_csv(__name__, ["Year", "Title", "Citation Count", "Author"])
def main(*args, **kwargs):

    for publication in Publication.select():
        yield [[
            publication.year,
            publication.title,
            publication.citation_count,
            publication.author,
        ]]

    raise StopIteration


def configure_parser(parser):
    parser.description = "Dump publication records."

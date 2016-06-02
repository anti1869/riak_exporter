"""
Entrypoint for the application
"""

import argparse
import os

from riak_exporter import RiakExporterServer


def main():
    # Add some args config
    parser = argparse.ArgumentParser(description='Riak KV metrics exporter to Prometheus.')
    parser.add_argument('--riak', dest='riak_stats', help='url of the Riak KV stats endpoint')
    parser.add_argument('--address', dest='address', help='address to serve on')
    parser.add_argument('--port', dest='port', help='port to bind')
    parser.add_argument('--endpoint', dest='endpoint', help='Prometheus metrics endpoint location')
    args = parser.parse_args()

    # Run exposing server
    exposer = RiakExporterServer(**vars(args))
    exposer.run()

import os

from riak_exporter import RiakExporterServer


def main():
    riak_stats = os.environ.get("RIAK_STATS", RiakExporterServer.DEFAULT_RIAK_STATS)
    exposer = RiakExporterServer(riak_stats)
    exposer.run()

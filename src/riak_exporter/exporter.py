"""
Riak stats bridge. Simply fetches data from Riak stats endpoint and exposed to binded port.
"""

from tornado.escape import json_decode
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPClient
from tornado.ioloop import IOLoop
from tornado.log import app_log
from tornado.web import RequestHandler, Application


class MainHandler(RequestHandler):
    """
    Mainpage with some meaningful stuff. Probably.
    """

    def get(self):
        self.write('<a href="/metrics">/metrics</a>')


class MetricsHandler(RequestHandler):
    """
    Endpoint handler.
    """

    DEFAULT_DATA = {}
    RIAK_REQUEST_TIMEOUT = 5.0
    RAISE_ERROR = True

    def __init__(self, *args, **kwargs):
        super(MetricsHandler, self).__init__(*args, **kwargs)
        self._client = AsyncHTTPClient()

    @coroutine
    def fetch_riak_stats(self, riak_stats):
        """
        Fetch Riak stats endpoint, deserialize JSON and return as Python dict.

        :param riak_stats: Riak stats endpoint address, accessible by http.
        :rtype: dict
        :return: Riak stats data
        """

        # TODO: Implement Riak fetch caching

        data = self.DEFAULT_DATA
        try:
            response = yield self._client.fetch(riak_stats, request_timeout=self.RIAK_REQUEST_TIMEOUT)
            data = json_decode(response.body)
        except (HTTPError, Exception) as e:
            app_log.error("Error fetching data from Riak", exc_info=True)
            if self.RAISE_ERROR:
                raise HTTPError(500, str(e))

        raise Return(data)

    def parse_riak_stats_data(self, riak_stats_data):
        """
        Filter key/values pairs from collected Riak stats, which may be meaningful for Prometheus.
        Convert value to float.

        :param riak_stats_data: Collected Riak stats object.
        :type riak_stats_data: dict
        :return: Generator of metrics that can be put into Prometheus snapshot.
        """
        for key, value in riak_stats_data.items():
            if isinstance(value, (int, float, bool)):
                prom_value = float(value)
                prom_str = "riak_{} {}".format(key, prom_value)
                yield prom_str

    @coroutine
    def get(self):
        """
        Process GET request most probably from Prometheus fetcher.

        :return: Reponse with prometheus metrics snapshot
        """
        riak_stats_data = yield self.fetch_riak_stats(self.application.riak_stats)
        prometheus = "\n".join(self.parse_riak_stats_data(riak_stats_data)) + "\n"
        self.set_header("Content-Type", "text/plain")
        self.write(prometheus)


class RiakExporterServer(object):
    """
    Basic server implementation that exposes metrics to Prometheus fetcher.
    """

    DEFAULT_RIAK_STATS = "http://localhost:8098/stats"
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8097
    DEFAULT_ENDPOINT = r"/metrics"

    def __init__(self, riak_stats=None, address=None, port=None, endpoint=None):
        self._riak_stats = riak_stats or self.DEFAULT_RIAK_STATS
        self._address = address or self.DEFAULT_HOST
        self._port = port or self.DEFAULT_PORT
        self._endpoint = endpoint or self.DEFAULT_ENDPOINT

    def make_app(self):
        app = Application([
            (r"/", MainHandler),
            (self._endpoint, MetricsHandler),
        ])
        app.riak_stats = self._riak_stats
        return app

    def print_info(self):
        print("Starting exporter on http://%s:%s%s" % (self._address, self._port, self._endpoint))
        print("Fetching stats from Riak at %s" % self._riak_stats)
        print("Press Ctrl+C to quit")

    def run(self):
        self.print_info()
        app = self.make_app()
        app.listen(self._port, address=self._address)
        loop = IOLoop.current()
        try:
            loop.start()
        except KeyboardInterrupt:
            loop.stop()

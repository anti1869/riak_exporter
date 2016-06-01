from tornado.escape import json_decode
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPClient
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application


class MainHandler(RequestHandler):

    def get(self):
        self.write('<a href="/metrics">/metrics</a>')


class MetricsHandler(RequestHandler):

    DEFAULT_DATA = "\n"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = HTTPClient()

    def fetch_riak_stats(self, riak_stats):
        """

        :param riak_stats:
        :rtype: dict
        :return:
        """
        data = self.DEFAULT_DATA
        try:
            response = self._client.fetch(riak_stats)
            data = json_decode(response.body)
        except HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            print("Error: " + str(e))
        except Exception as e:
            # Other errors are possible, such as IOError.
            print("Error: " + str(e))
        return data

    def parse_riak_stats_data(self, riak_stats_data):
        for key, value in riak_stats_data.items():
            if isinstance(value, (int, float, bool)):
                prom_value = float(value)
                prom_str = "{}: {}".format(key, prom_value)
                yield prom_str

    def get(self):
        riak_stats_data = self.fetch_riak_stats(self.application.riak_stats)
        prometheus = "\n".join(self.parse_riak_stats_data(riak_stats_data)) + "\n"
        self.set_header("Content-Type", "text/plain")
        self.write(prometheus)


class RiakExporterServer(object):

    DEFAULT_RIAK_STATS = "http://localhost:8098/stats"
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8888

    def __init__(self, riak_stats, host = None, port = None):
        self._host = host or self.DEFAULT_HOST
        self._port = port or self.DEFAULT_PORT
        self._riak_stats = riak_stats

    def make_app(self):
        app = Application([
            (r"/", MainHandler),
            (r"/metrics", MetricsHandler),
        ])
        app.riak_stats = self._riak_stats
        return app

    def print_info(self):
        print("Starting exporter on %s:%s" % (self._host, self._port))
        print("Fetching stats from Riak at %s" % self._riak_stats)
        print("Press Ctrl+C to quit")

    def run(self):
        self.print_info()
        app = self.make_app()
        app.listen(self._port, address=self._host)
        loop = IOLoop.current()
        try:
            loop.start()
        except KeyboardInterrupt:
            loop.stop()

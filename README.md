# Riak KV Metrics Exporter

Prometheus exporter for Riak metrics.
Supports Riak KV 2.x

It works simply by fetching available Riak /stats enpoint from the node, parsing its metrics 
and converting to format that Prometheus understands.

## Installing, configuring, and running

You can install exporter on the same node as Riak KV instance, or on separate machine.
To run, you must have ``Python`` and ``pip`` installed (Python 2 and 3 supported).

To install with ``pip``:

```
pip install riak_exporter
```

Then just:

```
riak-exporter --address=0.0.0.0 --port=8097 --riak=http://localhost:8098/stats --endpoint=/metrics
```

All arguments are optional.
 
## Daemonizing

Application intentionally does not daemonize itself. You are free to use your favorite method on your distribution.

## Status

Currently, this app is in early stages of development. Nothing more that simple ``/stats`` endpoint translation
is here. More features will (or will not follows) as long as I'll need them in my production setup.

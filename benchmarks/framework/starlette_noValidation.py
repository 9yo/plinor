"""
This file contains the Starlette implementation of the benchmarking

>  export WSGI_APP=benchmarks.framework.starlette_noValidation:app && poetry run gunicorn -c src/gunicorn.conf.py

1 WORKER
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.04ms  114.20us   3.97ms   88.50%
    Req/Sec     9.63k   393.33    10.01k    93.55%
  29707 requests in 3.10s, 2.61MB read
Requests/sec:   9582.36
Transfer/sec:    860.91KB

8 WORKERS
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   289.80us  168.86us   6.12ms   96.24%
    Req/Sec    34.44k     3.12k   38.84k    67.74%
  106183 requests in 3.10s, 9.32MB read
Requests/sec:  34252.22
Transfer/sec:      3.01MB
"""
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


async def get_data(request: Request) -> Response:
    return Response(status_code=200)


app = Starlette(
    debug=True,
    routes=[
        Route("/api/v1/data", endpoint=get_data, methods=["POST"]),
    ],
)

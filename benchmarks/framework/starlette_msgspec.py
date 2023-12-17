"""
This file contains the Starlette implementation of the benchmarking

>  export WSGI_APP=benchmarks.framework.starlette_msgspec:app && poetry run gunicorn -c src/gunicorn.conf.py

1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.12ms   98.89us   2.26ms   83.19%
    Req/Sec     8.98k   309.18     9.39k    80.65%
  27695 requests in 3.10s, 2.43MB read
Requests/sec:   8935.19
Transfer/sec:    802.77KB

8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   291.74us   89.03us   1.52ms   78.70%
    Req/Sec    33.50k     1.51k   35.53k    70.97%
  103280 requests in 3.10s, 9.06MB read
Requests/sec:  33319.93
Transfer/sec:      2.92MB

"""
from typing import Optional, Annotated

import msgspec
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


class DataModel(msgspec.Struct):
    ts: int
    a: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    b: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    c: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    d: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    e: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    f: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    A: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    B: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    C: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    D: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    E: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None
    F: Optional[Annotated[int, msgspec.Meta(ge=0, le=10)]] = None

    def __post_init__(self):
        if not any([self.a or self.A, self.b or self.B, self.c or self.C, self.d or self.D, self.e or self.E, self.f or self.F]):
            raise ValueError("At least one of a, b, c, d, e, f must be specified")
        self.a = self.a or self.A
        self.b = self.b or self.B
        self.c = self.c or self.C
        self.d = self.d or self.D
        self.e = self.e or self.E
        self.f = self.f or self.F


async def get_data(request: Request) -> Response:
    data = msgspec.json.decode(await request.body(), type=DataModel)
    return Response(status_code=200)


app = Starlette(
    debug=True,
    routes=[
        Route("/api/v1/data", endpoint=get_data, methods=["POST"]),
    ],
)

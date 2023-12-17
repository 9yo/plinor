"""
This file contains the Starlette implementation of the benchmarking

>  export WSGI_APP=benchmarks.db_insert.many_single_inserts:app && poetry run gunicorn -c src/gunicorn.conf.py

1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.18ms  254.89us   6.92ms   78.74%
    Req/Sec     4.60k   164.94     4.82k    80.65%
  14182 requests in 3.10s, 1.24MB read
Requests/sec:   4574.54
Transfer/sec:    410.99KB

8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.08ms  824.37us  16.43ms   98.45%
    Req/Sec     9.87k   823.53    10.46k    90.00%
  29449 requests in 3.00s, 2.58MB read
Requests/sec:   9815.83
Transfer/sec:      0.86MB
"""
import contextlib

import asyncpg
from asyncpg import Pool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

# db setup
connection_pool: Pool | None = None


async def setup_database():
    global connection_pool
    connection_pool = await asyncpg.create_pool(
        user='plinor_admin',
        password='plinor_admin',
        database='plinor',
        host='0.0.0.0',
        port=5432
    )


@contextlib.asynccontextmanager
async def lifespan(_):
    await setup_database()
    yield
    await connection_pool.close()


async def get_data(request: Request) -> Response:
    data = await request.json()
    ts = data.get("ts")
    a = data.get("a") or data.get("A")
    b = data.get("b") or data.get("B")
    c = data.get("c") or data.get("C")
    d = data.get("d") or data.get("D")
    e = data.get("e") or data.get("E")
    f = data.get("f") or data.get("F")

    # THIS SLOWS DOWN THE INSERTS 3 TIMES
    # if ts:
    #     ts = datetime.fromtimestamp(ts)

    # SQL TO TIMESTAMP SLOWS DOWN THE INSERTS 2 TIMES
    async with connection_pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO public.data_records (ts, a, b, c, d, e, f) VALUES (to_timestamp($1), $2, $3, $4, $5, $6, $7)",
            ts, a, b, c, d, e, f
        )

    return Response(status_code=200)


app = Starlette(
    debug=True,
    routes=[
        Route("/api/v1/data", endpoint=get_data, methods=["POST"]),
    ],
    lifespan=lifespan
)

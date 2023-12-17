"""
This file contains the Starlette implementation of the benchmarking

>  export WSGI_APP=benchmarks.db_insert.buffered_bulk_inserts:app && poetry run gunicorn -c src/gunicorn.conf.py

1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    10.15ms   30.97ms 187.73ms   92.05%
    Req/Sec     7.83k     1.70k    8.79k    89.29%
  22337 requests in 3.00s, 1.96MB read
Requests/sec:   7438.03
Transfer/sec:    668.26KB

8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.38ms   12.80ms 146.44ms   96.96%
    Req/Sec    31.24k     3.87k   37.54k    67.74%
  96308 requests in 3.10s, 8.45MB read
Requests/sec:  31069.67
Transfer/sec:      2.73MB
"""
import contextlib
from typing import Tuple

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


class BulkDataProcessor:
    def __init__(self, batch_size: int = 10000):
        self.batch_size = batch_size
        self.buffer = []

    async def add_data(self, data_row: Tuple[int, int, int, int, int, int]):
        self.buffer.append(data_row)
        if len(self.buffer) >= self.batch_size:
            await self.bulk_insert_to_db()
            self.buffer = []

    async def bulk_insert_to_db(self):
        async with connection_pool.acquire() as connection:
            await connection.executemany(
                "INSERT INTO public.data_records (ts, a, b, c, d, e, f) VALUES (to_timestamp($1), $2, $3, $4, $5, $6, $7)",
                self.buffer
            )

    async def flush(self):
        if self.buffer:
            await self.bulk_insert_to_db()
            self.buffer = []


bulk_data_processor = BulkDataProcessor()


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
    await bulk_data_processor.add_data((ts, a, b, c, d, e, f))

    return Response(status_code=200)


app = Starlette(
    debug=True,
    routes=[
        Route("/api/v1/data", endpoint=get_data, methods=["POST"]),
    ],
    lifespan=lifespan
)

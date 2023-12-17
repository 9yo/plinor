"""
PRINCIPLE CHANGES COMPARED TO THE ORIGINAL FILE:
- The timestamp is not converted to datetime\
- Using copy_records_to_table instead of executemany

This file contains the Starlette implementation of the benchmarking

>  export WSGI_APP=benchmarks.db_insert.buffered_bulk_inserts_ts_int:app && poetry run gunicorn -c src/gunicorn.conf.py

1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.86ms    4.41ms  52.03ms   97.34%
    Req/Sec     8.12k     0.86k    8.81k    93.33%
  24249 requests in 3.00s, 2.13MB read
Requests/sec:   8080.43
Transfer/sec:    725.98KB

8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   536.71us    2.33ms  49.26ms   98.57%
    Req/Sec    32.40k     3.51k   37.77k    70.00%
  96796 requests in 3.00s, 8.49MB read
Requests/sec:  32258.82
Transfer/sec:      2.83MB
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
            await connection.copy_records_to_table('data_records', records=self.buffer, columns=('ts', 'a', 'b', 'c', 'd', 'e', 'f'))

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

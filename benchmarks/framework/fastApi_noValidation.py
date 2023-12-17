"""
This file contains the FastAPI implementation of the benchmarking

>  export WSGI_APP=benchmarks.framework.fastApi_noValidation:app && poetry run gunicorn -c src/gunicorn.conf.py

1 WORKER
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.58ms  151.67us   4.33ms   86.85%
    Req/Sec     6.36k   251.29     6.71k    80.65%
  19599 requests in 3.10s, 1.72MB read
Requests/sec:   6322.75
Transfer/sec:    568.06KB

8 WORKERS
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   349.75us  122.11us   3.36ms   82.75%
    Req/Sec    28.44k     2.19k   31.00k    61.29%
  87686 requests in 3.10s, 7.69MB read
Requests/sec:  28284.05
Transfer/sec:      2.48MB
"""
from fastapi import APIRouter, FastAPI
from starlette.responses import Response

router = APIRouter()


@router.post("/data")
async def ingest_data(data_item: dict):
    return Response(status_code=200)


app = FastAPI()
app.include_router(router, prefix="/api/v1")

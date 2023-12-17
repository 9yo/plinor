"""
This file contains the FastAPI implementation of the benchmarking

>  export WSGI_APP=benchmarks.framework.fastApi_pydantic:app && poetry run gunicorn -c src/gunicorn.conf.py

1 WORKER
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.72ms  200.97us   7.08ms   91.72%
    Req/Sec     5.86k   275.24     6.14k    87.10%
  18055 requests in 3.10s, 1.58MB read
Requests/sec:   5823.40
Transfer/sec:    523.20KB

8 WORKERS
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Running 3s test @ http://0.0.0.0:9091/api/v1/data
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   364.30us  116.74us   3.94ms   80.67%
    Req/Sec    27.22k     1.47k   29.52k    63.33%
  81219 requests in 3.00s, 7.13MB read
Requests/sec:  27067.60
Transfer/sec:      2.37MB
"""
from fastapi import APIRouter, FastAPI
from pydantic import model_validator, AliasChoices, Field, BaseModel
from starlette.responses import Response

router = APIRouter()


class DataModel(BaseModel):
    ts: int = Field(..., description="Timestamp")
    a: int | None = Field(None, description="a", validation_alias=AliasChoices("a", "A"), gt=0, lt=10)
    b: int | None = Field(None, description="b", validation_alias=AliasChoices("b", "B"), gt=0, lt=10)
    c: int | None = Field(None, description="c", validation_alias=AliasChoices("c", "C"), gt=0, lt=10)
    d: int | None = Field(None, description="d", validation_alias=AliasChoices("d", "D"), gt=0, lt=10)
    e: int | None = Field(None, description="e", validation_alias=AliasChoices("e", "E"), gt=0, lt=10)
    f: int | None = Field(None, description="f", validation_alias=AliasChoices("f", "F"), gt=0, lt=10)

    @model_validator(mode="after")
    def check_at_least_one_field_is_specified(self):
        if not any([self.a, self.b, self.c, self.d, self.e, self.f]):
            raise ValueError("At least one of a, b, c, d, e, f must be specified")
        return self


@router.post("/data")
async def ingest_data(data_item: DataModel):
    return Response(status_code=200)


app = FastAPI()
app.include_router(router, prefix="/api/v1")

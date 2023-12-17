## Общие положения:
1. Для замеров производительности использовался [wrk](https://github.com/wg/wrk). 36к stars.
2. Хост - Apple M1 PRO, 16GB RAM.
3. Все замеры производились с повторением 5 раз. Аномальные результаты исключены.

## Wrk Configuration:
В рандомности запросов нет необходимости, главное использовать максимальный размер данных за 
один запрос.
```lua 
wrk.method = "POST"
wrk.body   = '{"a": 1,"b": 7,"c":3,"d":9,"e":5,"f":2,"ts":1111111}'
wrk.headers["Content-Type"] = "application/json"
```


## Замеры производительности - Framework:
### FastAPI with no validation:
```bash
> export WSGI_APP=benchmarks.framework.fastApi_noValidation:app && poetry run gunicorn -c src/gunicorn.conf.py

# 1 WORKER
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:   6322.75

#8 WORKERS
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:  28284.05
```

### FastAPI with Pydantic validation:
```bash
>  export WSGI_APP=benchmarks.framework.fastApi_pydantic:app && poetry run gunicorn -c src/gunicorn.conf.py

# 1 WORKER
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:   5823.40

# 8 WORKERS
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:  27067.60
```

### Starlette with no validation:
```bash
>  export WSGI_APP=benchmarks.framework.starlette_noValidation:app && poetry run gunicorn -c src/gunicorn.conf.py

# 1 WORKER
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:   9582.36

# 8 WORKERS
> ./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:  34252.22
```

### Starlette with [MSGSPEC](https://github.com/jcrist/msgspec) validation:
```bash

>  export WSGI_APP=benchmarks.framework.starlette_msgspec:app && poetry run gunicorn -c src/gunicorn.conf.py

# 1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Requests/sec:   8935.19

# 8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
Requests/sec:  33319.93
```

## Замеры производительности - DB INSERT:
1. В качестве идеальной среды будет использоваться кофигурация без валидации, с starlette.
2. По замерам становится понятно, что операция вставки в базу данных уменьшает производительность,
поэтому задача - приблизиться к результатам без вставки в базу данных.
3. В качестве базы данных используется PostgreSQL 14, в качестве драйвера - asyncpg.

### TLDR:
Используем вставку в базу данных с буферизацией, вместо множества одиночных запросов.
Храним ts как SQL TIMESTAMP, так как прирост производительности не существенный.

Выводы на которых базируется TLDR:

1. Вместо отправки множество одиночных запросов, отправлять один запрос с множеством данных.
2. Количество данных в одном запросе должно вычисляться динамически, но сейчас это 10000.
3. Хранение ts как int, дает прирост, но не существенный.

### Starlette with no validation and multiple single inserts:
```bash
>  export WSGI_APP=benchmarks.db_insert.many_single_inserts:app && poetry run gunicorn -c src/gunicorn.conf.py

# 1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:   4574.54

# 8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:   9815.83
```

### Starlette with no validation and buffered bulk inserts, 10000 batch size:
```bash
>  export WSGI_APP=benchmarks.db_insert.buffered_bulk_inserts:app && poetry run gunicorn -c src/gunicorn.conf.py

# 1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:   7438.03

# 8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:  31069.67
```

### Starlette with no validation and buffered bulk inserts, 10000 batch size, storing ts as int:
```bash
PRINCIPLE CHANGES COMPARED TO PREVIOUS VERSION:
- The timestamp is not converted to datetime
- Using copy_records_to_table instead of executemany

>  export WSGI_APP=benchmarks.db_insert.buffered_bulk_inserts_ts_int:app && poetry run gunicorn -c src/gunicorn.conf.py

# 1 WORKER
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:   8080.43

# 8 WORKERS
./wrk -s post.lua -c10 -d3s -t1 http://0.0.0.0:9091/api/v1/data
...
Requests/sec:  32258.82
```
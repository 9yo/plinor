"""
Модуль конфигурации gunicorn
"""
import os
from os import kill
from signal import SIGINT

from gunicorn.workers.base import Worker

wsgi_app = os.getenv("WSGI_APP", "src.main:app")

worker_class = "uvicorn.workers.UvicornWorker"
bind = f"0.0.0.0:9091"
workers = 8
reload = True


def worker_int(worker: Worker) -> None:
    kill(worker.pid, SIGINT)

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from src.connection import bulk_data_processor, lifespan


async def get_data(request: Request) -> Response:
    data = await request.json()
    ts = data.get("ts")
    a = data.get("a") or data.get("A")
    b = data.get("b") or data.get("B")
    c = data.get("c") or data.get("C")
    d = data.get("d") or data.get("D")
    e = data.get("e") or data.get("E")
    f = data.get("f") or data.get("F")

    await bulk_data_processor.add_data((ts, a, b, c, d, e, f))

    return Response(status_code=200)


app = Starlette(
    debug=True,
    routes=[
        Route("/api/v1/data", endpoint=get_data, methods=["POST"]),
    ],
    lifespan=lifespan
)

import contextlib
from typing import Tuple

import asyncpg
from asyncpg import Pool

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

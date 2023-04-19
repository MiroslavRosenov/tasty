from __future__ import annotations
import asyncio

import json
import os
import asyncpg

from quart import Quart
from typing import Optional, Tuple, Type, TypeVar, Any, List

from ext.postgres.tables import *

Record = TypeVar("Record", bound=asyncpg.Record)

class Acquire:
    def __init__(self, db: PostgreSQLClient, *, timeout: float = None):
        self._type: Type[PostgreSQLClient] = db.__class__
        self._pool: asyncpg.Pool = db._pool
        self._timeout: float = timeout
        self._db: Optional[PostgreSQLClient] = None

    async def _acquire(self) -> PostgreSQLClient:
        accquired_connection = await self._pool._acquire(self._timeout)
        return self._type(pool=self._pool, accquired_connection=accquired_connection)

    async def __aenter__(self) -> PostgreSQLClient:
        self._db = self._acquire()
        return self._db

    async def __aexit__(self) -> None:
        await self._db.release()

    def __await__(self):
        return self._acquire().__await__()

class PostgreSQLClient:
    def __init__(self, app: Quart) -> None:
        self._app = app
        self._pool: Optional[asyncpg.Pool] = None
        self._accquired_connection: Optional[asyncpg.Connection] = None
        self._ready = asyncio.Event()

    def acquire(self, *, timeout: int = None):
        return Acquire(self, timeout=timeout)

    async def ready(self) -> None:
        await self._ready.wait()

    @classmethod
    async def connect(cls, app: Quart, **kwargs) -> PostgreSQLClient:
        kwargs = kwargs or {
            "user": os.getenv("PSQL_USER"),
            "password": os.getenv("PSQL_PASSWORD"),
            "database": os.getenv("PSQL_DB"),
            "host": os.getenv("PSQL_HOST"),
        }

        self = cls(app)
        await self.setup(**kwargs)
        return self

    async def _execute(self, method: str, *args, **kwargs) -> Any:
        connection = self._accquired_connection or await self._pool.acquire()

        ret = await getattr(connection, method)(*args, **kwargs)

        if not self._accquired_connection:
            await self._pool.release(connection)

        return ret

    async def setup(self, **kwargs) -> None:
        def _encode_jsonb(value: str):
            return json.dumps(value)

        def _decode_jsonb(value: str):
            return json.loads(value)

        async def init(connection: asyncpg.Connection):
            await connection.set_type_codec(
                "jsonb",
                schema="pg_catalog",
                encoder=_encode_jsonb,
                decoder=_decode_jsonb,
                format="text",
            )

        self._pool = await asyncpg.create_pool(init=init, **kwargs)
        self._ready.set()

    async def close(self) -> None:
        if self._accquired_connection:
            await self.release()

        await self._pool.close()

    async def release(self, *, timeout: int = None) -> None:
        if not self._accquired_connection:
            return

        await self._pool.release(self._accquired_connection, timeout=timeout)

    async def execute(self, query, *args, timeout: float = None) -> None:
        return await self._execute("execute", query, *args, timeout=timeout)

    async def executemany(
        self, query: str, args: List[Tuple[Any, ...]], *, timeout: float = None
    ) -> Any:
        return await self._execute("executemany", query, args, timeout=timeout)

    async def fetch(
        self, query: str, *args, timeout: float = None, value: bool = False
    ) -> List[Record]:
        return await self._execute(
            "fetch" if not value else "fetchval", query, *args, timeout=timeout
        )

    async def fetchrow(self, query: str, *args, timeout: float = None) -> Record:
        return await self._execute("fetchrow", query, *args, timeout=timeout)

    async def fetchval(
        self, query: str, *args: Any, column: int = 0, timeout: Optional[float] = None
    ) -> Any:
        return await self._execute("fetchval", query, *args, column=column, timeout=timeout)
    
    @property
    def dishes(self):
        return Dishes(self)
    
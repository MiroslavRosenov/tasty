from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ext.postgres.base import PostgreSQLClient

class Table:
    def __init__(self, database):
        self.database: PostgreSQLClient = database
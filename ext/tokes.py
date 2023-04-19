from quart import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature 
from typing import Optional

from ext.postgres.base import PostgreSQLClient

async def generate(email: str, insert: bool = True) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = serializer.dumps(email, salt=current_app.config["SECURITY_PASSWORD_SALT"])
    pool: PostgreSQLClient = current_app.db

    if insert:
        await pool.execute("INSERT INTO tokens(token, email) VALUES ($1, $2)", token, email)
    return token

async def confirm(token: str, expiration: int = 3600) -> Optional[str]:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    pool: PostgreSQLClient = current_app.db
    
    if await pool.fetchrow("SELECT * FROM tokens WHERE token = $1", token):
        return serializer.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=expiration)
    raise BadSignature("Token not found in the database!")


from quart import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature 
from typing import Optional

def generate(email: str, insert: bool = True) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = serializer.dumps(email, salt=current_app.config["SECURITY_PASSWORD_SALT"])

    if insert:
        with current_app.db.cursor(dictionary=True) as cur:
            query = "INSERT INTO tokens(token, email) VALUES (%s, %s)"
            cur.execute(query, (token, email))
            current_app.db.commit()
    return token

def confirm(token: str, expiration: int = 3600) -> Optional[str]:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    
    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        cur.execute("SELECT * FROM tokens WHERE token = %s", (token,))
        if cur.fetchone():
            return serializer.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=expiration)
        raise BadSignature("Token not found in the database!")


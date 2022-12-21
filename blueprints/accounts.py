import hashlib
import json

from quart_auth import AuthUser, login_required, login_user, logout_user, current_user
from quart import Blueprint, render_template, redirect, url_for, request, current_app

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from ext.base import cursor_to_dict

from ext.tokes import generate, confirm
from mysql.connector.errors import IntegrityError

accounts = Blueprint("accounts", __name__)

MAIL_BODY = "http://127.0.0.1:8000/confirm/{token}"

@accounts.route("/signin", methods=["GET", "POST"])
async def signin() -> None:
    if request.method == "GET":
        return await render_template("signin.html")
    else:
        data = json.loads(await request.data)

        query = "SELECT * FROM accounts WHERE email = %s AND password = %s"
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            cur.execute(query, (data.get("email"), hashlib.sha256(data.get("password").encode("utf-8")).hexdigest()))
            
            if not (resp := cur.fetchone()):
                return {
                    "error": "Акаунтът не беше намерен"
                }, 403
            if not resp["confirmed"]:
                return {
                    "error": "Моля, потвърдете акаунта си" 
                }, 403
            login_user(AuthUser(resp["id"]), data.get("remember"))
            return "", 200

@accounts.route("/signup", methods=["GET", "POST"])
async def signup() -> None:
    if request.method == "GET":
        return await render_template("signup.html")
    else:
        data = json.loads(await request.data)

        query = "INSERT INTO accounts (email, firstName, lastName, password) VALUES (%s, %s, %s, %s)"
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            email = data.get("email")
            try:
                cur.execute(query, (email, data.get("firstName"), data.get("lastName"), hashlib.sha256(data.get("password").encode("utf-8")).hexdigest()))
            except IntegrityError:
                return {
                    "error": "Имейлът вече се използва!" 
                }, 500
            else:
                token = generate(email)
                await current_app.mail.send(
                    email, "Моля, потвърдете регистрацията си", MAIL_BODY.format(token=token)
                )
                current_app.db.commit()

                return {
                    "message": "Вие успешно създадохте своя акаунт! Моля, потвърдете го с линка, изпратен на вашия имейл." 
                }, 200

@accounts.get("/signout")
async def signout() -> None:
    logout_user()
    return redirect(url_for("recipes.index"))

@accounts.route("/password-reset")
async def password_reset() -> None:
    if request.method == "GET":
        return await render_template("password_reset.html")

@accounts.route("/confirm/<string:token>")
async def confirm_account(token: str) -> None:
    try:
        email = confirm(token)
    except SignatureExpired:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = serializer.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"])
        
        with current_app.db.cursor() as cur:
            query = "UPDATE tokens SET token = %s WHERE email = %s"
            cur.execute(query, ((token := generate(email, False)), email))
            current_app.db.commit()
        
        await current_app.mail.send(
            email, "Моля, потвърдете регистрацията си", MAIL_BODY.format(token=token)
        )
        return await render_template("exception.html", details={
            "title": "Не можахме да потвърдим акаунта ви!",
            "message": "Линкът, който предоставихте, е изтекъл, изпратете ви нов"
        })
    except BadSignature:
        return await render_template("exception.html", details={
            "title": "Не можахме да потвърдим акаунта ви!",
            "message": "Линкът, който предоставихте е невалидна!"
        })
    else:
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "DELETE FROM tokens WHERE token = %s" 
            cur.execute(query, (token,))

            query = "UPDATE accounts SET confirmed = true WHERE email = %s"
            cur.execute(query, (email,))
            current_app.db.commit()

            query = "SELECT * FROM accounts WHERE email = %s"
            cur.execute(query, (email,))
            resp = cur.fetchone()

            login_user(AuthUser(resp["id"]), True)

@accounts.route("/bookmarks")
@login_required
async def bookmarks() -> None:
    with current_app.db.cursor(prepared=True, buffered=False) as cur:
        query = "SELECT * FROM dishes WHERE id IN (SELECT dish FROM bookmarks WHERE account = %s) ORDER BY timestamp DESC"
        cur.execute(query, (current_user.auth_id,))
        return await render_template("bookmarks.html", results=cursor_to_dict(cur))

import hashlib
import json
import contextlib
import typing

from quart_auth import AuthUser, login_required, login_user, logout_user, current_user
from quart import Blueprint, render_template, redirect, url_for, request, current_app

from smtplib import SMTPRecipientsRefused
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from ext.tokes import generate, confirm
from asyncpg import UniqueViolationError

if typing.TYPE_CHECKING:
    from ext.postgres.base import PostgreSQLClient
else:
    from asyncpg.pool import Pool as PostgreSQLClient

accounts = Blueprint("accounts", __name__)

MAIL_BODY = "https://vkusno.noit.eu/confirm/{token}"

@accounts.route("/signin", methods=["GET", "POST"])
async def signin() -> None:
    if request.method == "GET":
        return await render_template("signin.html")
    
    data = json.loads(await request.data)
    pool: PostgreSQLClient = current_app.db
    
    if not (resp := await pool.fetchrow(
        "SELECT * FROM accounts WHERE email = $1 AND password = $2",
        data.get("email"), 
        hashlib.sha256(data.get("password").encode("utf-8")).hexdigest()

    )):
        return {
            "error": "Акаунтът не беше намерен"
        }, 404
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
    
    data = json.loads(await request.data)
    pool: PostgreSQLClient = current_app.db

    try:
        await pool.execute(
            "INSERT INTO accounts (email, firstName, lastName, password) VALUES ($1, $2, $3, $4)",
            (email := data.get("email")), data.get("firstName"), data.get("lastName"), hashlib.sha256(data.get("password").encode("utf-8")).hexdigest()
        )
    except UniqueViolationError:
        return {
            "error": "Имейлът вече се използва!" 
        }, 500
    else:
        with contextlib.suppress(SMTPRecipientsRefused):
            await current_app.mail.send(
                email, "Моля, потвърдете регистрацията си", MAIL_BODY.format(token=await generate(email))
            )

        return {
            "message": "Вие успешно създадохте своя акаунт! Моля, потвърдете го с линка, изпратен на вашия имейл." 
        }, 200

@accounts.get("/signout")
async def signout() -> None:
    logout_user()
    return redirect(url_for("index"))

@accounts.get("/confirm/<string:token>")
async def confirm_account(token: str) -> None:
    pool: PostgreSQLClient = current_app.db
    
    try:
        email = await confirm(token)
    except SignatureExpired:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = serializer.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"])
        
        await pool.execute("UPDATE tokens SET token = $1 WHERE email = $2", (new_token := generate(email, False)), email)
        await current_app.mail.send(email, "Моля, потвърдете регистрацията си във Вкусно!", MAIL_BODY.format(token=new_token))
        
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
        await pool.execute("DELETE FROM tokens WHERE token = $1", token)
        login_user(AuthUser(await pool.fetchval("UPDATE accounts SET confirmed = true WHERE email = $1 RETURNING id", email)), True)
        return redirect("/")

@accounts.get("/bookmarks")
@login_required
async def bookmarks() -> None:
    pool: PostgreSQLClient = current_app.db

    resp = await pool.fetch("SELECT * FROM dishes WHERE id IN (SELECT dish FROM bookmarks WHERE account = $1) ORDER BY timestamp DESC", current_user.auth_id)
    return await render_template("bookmarks.html", results=resp)

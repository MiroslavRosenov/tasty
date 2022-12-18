import hashlib


from quart_auth import AuthUser, login_required, login_user, current_user
from quart import Blueprint, render_template, flash, redirect, url_for, request, current_app

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from ext.tokes import generate, confirm
from mysql.connector.errors import IntegrityError

accounts = Blueprint("accounts", __name__)

MAIL_BODY = "http://127.0.0.1:8000/confirm/{token}"

@accounts.route("/signin", methods=["GET", "POST"])
async def signin() -> None:
    if request.method == "GET":
        return await render_template("signin.html")
    else:
        form = await request.form

        query = "SELECT * FROM accounts WHERE email = %s AND password = %s"
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            cur.execute(query, (form.get("email"), hashlib.sha256(form.get("password").encode("utf-8")).hexdigest()))
            if not (resp := cur.fetchone()):
                await flash("Акаунтът не беше намерен", "error")
                return await render_template("signin.html")
            if not resp["confirmed"]:
                await flash("Моля, потвърдете акаунта си", "error")
                return await render_template("signin.html")
            
            login_user(AuthUser(resp["id"]), form.get("remember"))
            return redirect(url_for("recipes.index"))

@accounts.route("/signup", methods=["GET", "POST"])
async def signup() -> None:
    if request.method == "GET":
        return await render_template("signup.html")
    else:
        form = await request.form

        query = "INSERT INTO accounts (id, email, firstName, lastName, password) VALUES (%s, %s, %s, %s, %s)"
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            email = form.get("email")
            try:
                cur.execute(query, (hashlib.sha256(email.encode("utf-8")).hexdigest(), email, form.get("firstName"), form.get("lastName"), hashlib.sha256(form.get("password").encode("utf-8")).hexdigest()))
            except IntegrityError:
                await flash("Имейлът вече се използва!", "error")
                return await render_template("signup.html")
            else:
                token = generate(email)
                await current_app.mail.send(
                    email, "Моля, потвърдете регистрацията си", MAIL_BODY.format(token=token)
                )
                current_app.db.commit()

                await flash("Вие успешно създадохте своя акаунт! Моля, потвърдете го с линка, изпратен на вашия имейл.", "success")
                return await render_template("signup.html")

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
        await flash("Линкът е изтекъл, изпратен е нов!", "error")
        return await render_template("signin.html")
    except BadSignature:
        await flash("Невалиден линк", "error")
        return await render_template("signin.html")
    else:
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "DELETE FROM tokens WHERE token = %s" 
            cur.execute(query, (token,))

            query = "UPDATE accounts SET confirmed = true WHERE email = %s"
            cur.execute(query, (email,))
            current_app.db.commit()

            await flash("Успешно потвърдихте акаунта си ", "success")
            return await render_template("signin.html")

@accounts.route("/bookmarks")
@login_required
async def bookmarks() -> None:
    return await render_template("bookmarks.html")
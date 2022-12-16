import dotenv
import hashlib
import os

from mysql.connector import MySQLConnection
from mysql.connector.errors import IntegrityError

from quart import Quart, render_template, abort, flash, redirect, url_for, request, session
from quart_auth import AuthManager, AuthUser, login_required, login_user, current_user

from ext.translator import Translator
from ext.base import get_recipe, search_recipe
from ext.tokes import generate, confirm
from ext.mail import EmailHandler

app = Quart(__name__)
app.config["SECURITY_PASSWORD_SALT"] = "ffe2d77f8f34dd3e382569c525bb854853e2b42a98fb47927d9a7b7a881f0b04"
app.config["SECRET_KEY"] = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

auth = AuthManager()
translate = Translator().translate

@app.route("/", methods=["GET", "POST"])
async def index() -> None:
    if request.method == "GET":
        with app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "SELECT * FROM recipe_details ORDER BY last_looked DESC LIMIT 6;"
            cur.execute(query)
            resp = cur.fetchall()

        return await render_template("index.html", data={"results": resp})

    if request.method == "POST":
        recipe = translate((await request.form).get("recipe"), "en", "bg")
        data = await search_recipe(query=recipe)
        print(recipe)
        
        if data.get("error", 0) == 404:
            return await render_template("404.html")

        data["originalSearch"] = (await request.form).get("recipe")
        return await render_template("recipes.html", data=data)

@app.route("/recipe/<int:id>", methods=["GET"])
async def recipe(id: int) -> None:
    return await render_template("details.html", data=await get_recipe(id=id))

@app.route("/signin", methods=["GET", "POST"])
async def signin() -> None:
    if request.method == "GET":
        return await render_template("signin.html")
    else:
        form = await request.form

        query = "SELECT * FROM accounts WHERE email = %s AND password = %s"
        with app.db.cursor(dictionary=True, buffered=False) as cur:
            cur.execute(query, (form.get("email"), hashlib.sha256(form.get("password").encode("utf-8")).hexdigest()))
            if not (resp := cur.fetchone()):
                await flash("Акаунтът не беше намерен", "error")
                return await render_template("signin.html")
            if not resp["confirmed"]:
                await flash("Моля, потвърдете акаунта си", "error")
                return await render_template("signin.html")
            
            login_user(AuthUser(resp["id"]), form.get("remember"))
            return redirect(url_for("index"))

@app.route("/signup", methods=["GET", "POST"])
async def signup() -> None:
    if request.method == "GET":
        return await render_template("signup.html")
    else:
        form = await request.form

        query = "INSERT INTO accounts (id, email, firstName, lastName, password) VALUES (%s, %s, %s, %s, %s)"
        with app.db.cursor(dictionary=True, buffered=False) as cur:
            email = form.get("email")
            try:
                cur.execute(query, (hashlib.sha256(email.encode("utf-8")).hexdigest(), email, form.get("firstName"), form.get("lastName"), hashlib.sha256(form.get("password").encode("utf-8")).hexdigest()))
            except IntegrityError:
                await flash("Имейлът вече се използва!", "error")
                return await render_template("signup.html")
            else:
                token = generate(email)
                await app.mail.send(
                    email, "Моля, потвърдете регистрацията си", f"127.0.0.1/activate/{token}"
                )
                app.db.commit()

                await flash("Вие успешно създадохте своя акаунт! Моля, потвърдете го с линка, изпратен на вашия имейл.", "success")
                return await render_template("signup.html")

@app.route("/activate/<string:token>")
async def activate(token: str) -> None:
    if (email := confirm(token)):
        with app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "SELECT * FROM accounts WHERE email = %s" 
            cur.execute(query, (email,))
            resp = cur.fetchone()

            if resp["confirmed"]:
                await flash("Вашият акаунт вече е потвърден", "error")
                return await render_template("signin.html")
            else:
                query = "UPDATE accounts SET confirmed = true WHERE email = %s"
                cur.execute(query, (email,))
                app.db.commit()

                await flash("Успешно потвърдихте акаунта си ", "success")
                return await render_template("signin.html")
    else:
        await flash("Невалиден линк", "error")
        return await render_template("signin.html")

@login_required
@app.route("/bookmarks")
async def bookmarks() -> None:
    if request.method == "GET":
        if not session.get("auth_state"):
            abort(403)
            
        return await render_template("bookmarks.html")


if __name__ == "__main__":
    dotenv.load_dotenv()
    app.db = MySQLConnection(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        database=os.getenv("MYSQL_DATABASE")
    )

    app.mail = EmailHandler(
        os.getenv("SMTP_HOST"),
        os.getenv("SMTP_PORT"),
        os.getenv("SMTP_EMAIL"),
        os.getenv("SMTP_PASSWORD")
    )

    auth.init_app(app)
    app.run(debug=True, use_reloader=True, port=8000)
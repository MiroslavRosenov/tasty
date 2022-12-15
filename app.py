import dotenv
import hashlib

from mysql.connector import MySQLConnection
from mysql.connector.errors import IntegrityError
from quart import Quart, render_template, abort, flash, redirect, url_for, request, session
from ext.base import get_recipe, search_recipe
from deep_translator import GoogleTranslator

app = Quart(__name__)
app.secret_key = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
translate = GoogleTranslator("bg", "en").translate

@app.route("/", methods=["GET", "POST"])
async def index() -> None:
    if request.method == "GET":
        with app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "SELECT * FROM recipe_details ORDER BY last_looked DESC LIMIT 6;"
            cur.execute(query)
            resp = cur.fetchall()

        return await render_template("index.html", data={"results": resp, "auth": bool(session.get("auth", False))})

    if request.method == "POST":
        recipe = translate((await request.form).get("recipe"))
        data = await search_recipe(query=recipe)
        
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
        with app.db.cursor(dictionary=True) as cur:
            cur.execute(query, (form.get("email"), hashlib.sha256(form.get("password").encode("utf-8")).hexdigest()))
            if not (resp := cur.fetchone()):
                await flash("Акаунтът не беше намерен", "error")
                return await render_template("signin.html")
            session["auth"] = resp["id"]
            return redirect(url_for("/account"))


@app.route("/signup", methods=["GET", "POST"])
async def signup() -> None:
    if request.method == "GET":
        return await render_template("signup.html")
    else:
        form = await request.form

        query = "INSERT INTO accounts (id, email, firstName, lastName, password) VALUES (%s, %s, %s, %s, %s)"
        with app.db.cursor(dictionary=True) as cur:
            
            try:
                cur.execute(query, (hashlib.sha256(form.get("email").encode("utf-8")).hexdigest(), form.get("email"), form.get("firstName"), form.get("lastName"), hashlib.sha256(form.get("password").encode("utf-8")).hexdigest()))
            except IntegrityError:
                await flash("Имейлът вече се използва!", "error")
                return await render_template("signup.html")
            else:
                app.db.commit()

@app.route("/bookmarks")
async def bookmarks() -> None:
    if request.method == "GET":
        if not session.get("auth_state"):
            abort(403)
            
        return await render_template("bookmarks.html")


if __name__ == "__main__":
    dotenv.load_dotenv()
    app.db = MySQLConnection(
        host ="127.0.0.1",
        user ="root",
        database="tasty"
    )

    app.run(debug=True, use_reloader=True, port=8000)
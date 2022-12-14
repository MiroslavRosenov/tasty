import dotenv
from mysql.connector import MySQLConnection, cursor
from quart import Quart, request, render_template
from ext.base import get_recipe, search_recipe
from deep_translator import GoogleTranslator

app = Quart(__name__)
app.jinja_env.filters["translate"] = GoogleTranslator("en", "bg").translate
translate = GoogleTranslator("bg", "en").translate

@app.route("/", methods=["GET", "POST"])
async def index() -> None:
    if request.method == "GET":
        with app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "SELECT * FROM recipe_details ORDER BY last_looked DESC LIMIT 6;"
            cur.execute(query)
            resp = cur.fetchall()

        return await render_template("index.html", data={"results": resp})

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

if __name__ == "__main__":
    dotenv.load_dotenv()
    app.db = MySQLConnection(
        host ="127.0.0.1",
        user ="root",
        database="tasty"
    )

    app.run(debug=True, use_reloader=True, port=8000)
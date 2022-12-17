from quart import Blueprint, render_template, flash, redirect, url_for, request, current_app

from ext.translator import Translator
from ext.base import get_recipe, search_recipe

recipes = Blueprint("recipes", __name__)
translate = Translator().translate

@recipes.route("/", methods=["GET", "POST"])
async def index() -> None:
    if request.method == "GET":
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "SELECT * FROM recipe_details ORDER BY last_looked DESC LIMIT 9;"
            cur.execute(query)
            resp = cur.fetchall()

        return await render_template("index.html", data={"results": resp})

    if request.method == "POST":
        recipe = translate((await request.form).get("recipe"), "en", "bg")
        data = await search_recipe(query=recipe)
        
        if data.get("error", 0) == 404:
            return await render_template("404.html")

        data["originalSearch"] = (await request.form).get("recipe")
        return await render_template("recipes.html", data=data)

@recipes.route("/recipe/<int:id>", methods=["GET"])
async def recipe(id: int) -> None:
    return await render_template("details.html", data=await get_recipe(id=id))
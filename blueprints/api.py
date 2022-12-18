import json
from quart import Blueprint, render_template, request, current_app

from ext.translator import Translator
from ext.base import get_recipe, search_recipe

api = Blueprint("api", __name__, url_prefix="/api")
translate = Translator().translate

@api.post("/searchRecipe")
async def search() -> None:
    data = json.loads(await request.data)
    return await search_recipe(query=translate(data.get("recipe"), "en", "bg"))

@api.get("/recentRecipes")
async def recent() -> None:
    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        query = "SELECT name, id, readyInMinutes, imageUrl FROM recipe_details ORDER BY last_looked DESC LIMIT 12;"
        cur.execute(query)
        return {"results": cur.fetchall()}

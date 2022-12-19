from quart import Blueprint, jsonify, render_template, request, current_app

from ext.translator import Translator
from ext.base import get_recipe, search_recipe

dishes = Blueprint("recipes", __name__)
translate = Translator().translate

@dishes.get("/")
async def index() -> None:
    # return str(await search_recipe(["eggs", "bacon", "muffins"]))
    return await render_template("index.html")

@dishes.get("/dishes/<int:id>")
async def dish(id: int) -> None:
    return await render_template("dish.html", data=await get_recipe(id=id))
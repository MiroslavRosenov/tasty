from quart import Blueprint, render_template, flash, redirect, url_for, request, current_app

from ext.translator import Translator
from ext.base import get_recipe, search_recipe

dishes = Blueprint("recipes", __name__)
translate = Translator().translate

@dishes.get("/")
async def index() -> None:
    return await render_template("index.html")

@dishes.get("/dishes/<int:id>")
async def dish(id: int) -> None:
    return await render_template("dish.html", data=await get_recipe(id=id))
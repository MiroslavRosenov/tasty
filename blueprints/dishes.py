from quart import Blueprint, render_template
from ext.base import recipe_details

dishes = Blueprint("dishes", __name__)

@dishes.get("/search")
async def search() -> None:
    return await render_template("search.html")

@dishes.get("/dishes/<int:id>")
async def dish(id: int) -> None:
    return await render_template("dish.html", data=await recipe_details(id=id))
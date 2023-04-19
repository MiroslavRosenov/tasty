from quart import Blueprint, current_app, render_template
from ext.postgres.base import PostgreSQLClient

dishes = Blueprint("dishes", __name__)

@dishes.get("/search")
async def search() -> None:
    return await render_template("search.html")

@dishes.get("/dishes/<int:id>")
async def dish(id: int) -> None:
    pool: PostgreSQLClient = current_app.db
    return await render_template("dish.html", data=dict(await pool.dishes.get(id)))
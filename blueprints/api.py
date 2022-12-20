import json
import hashlib

from quart import Blueprint, render_template, request, current_app
from quart_auth import AuthUser, login_user

from ext.translator import Translator
from ext.base import cursor_to_dict, search_tags

api = Blueprint("api", __name__, url_prefix="/api")
translate = Translator().translate

@api.post("/searchRecipe")
async def search() -> None:
    data = json.loads(await request.data)
    return await search_tags([translate(x["value"], "en", "bg") for x in data["ingredients"]])

@api.get("/recentRecipes")
async def recent() -> None:
    with current_app.db.cursor(prepared=True, buffered=False) as cur:
        query = "SELECT id, title, imageUrl, ingredients FROM dishes ORDER BY timestamp DESC LIMIT 12;"
        cur.execute(query)
        return {"results": cursor_to_dict(cur)}

@api.route("/bookmarks", methods=["POST", "PUT" "DELETE"])
async def favourites() -> None:
    data = json.loads(await request.data)
    
    if request.method == "POST":
        return {
            "count": 0,
            "state": True 
        }
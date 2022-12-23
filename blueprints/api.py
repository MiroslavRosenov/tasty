import json
import contextlib

from quart import Blueprint, request, current_app
from quart_auth import current_user

from ext.translator import Translator
from ext.base import cursor_to_dict, search_tags
from mysql.connector.errors import IntegrityError

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

@api.route("/bookmarks", methods=["POST", "PUT", "DELETE"])
async def bookmarks() -> None:
    if not current_user.auth_id:
        return {
            "error": "Трябва да сте влезли в акаунта си, за да добавите това ястие към любимите ви ястия!"
        }, 401
        
    data = json.loads(await request.data)
    if request.method == "POST":
        query = "SELECT * FROM bookmarks WHERE account = %s AND dish = %s"
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            cur.execute(query, (current_user.auth_id, data.get("id"),))
            return {"state": bool(cur.fetchone())}

    if request.method == "PUT":
        query = "INSERT INTO bookmarks(account, dish) VALUES(%s, %s)"
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            with contextlib.suppress(IntegrityError):
                cur.execute(query, (current_user.auth_id, data.get("id"),))
                current_app.db.commit()
            return "", 200

    if request.method == "DELETE":
        query = "DELETE FROM bookmarks WHERE account = %s AND dish = %s"
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            cur.execute(query, (current_user.auth_id, data.get("id"),))
            current_app.db.commit()
            return "", 200


@api.post("/bookmarksCount")
async def bookmarksCount() -> None:
    data = json.loads(await request.data)
    query = "SELECT COUNT(*) as amount FROM bookmarks WHERE dish = %s"
    
    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        cur.execute(query, (data.get("id"),))
        resp = cur.fetchone()

        return {"count": resp["amount"]}
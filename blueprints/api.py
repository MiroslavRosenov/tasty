import json
import contextlib

from quart import Blueprint, request, current_app
from quart_auth import current_user, login_required
from typing import Dict
from collections import Counter

from ext.translator import Translator
from ext.base import search_tags
from ext.postgres.base import PostgreSQLClient

api = Blueprint("api", __name__, url_prefix="/api")
translate = Translator().translate

@api.post("/searchRecipe")
async def search() -> None:
    data: Dict = json.loads(await request.data)
    return await search_tags([translate(x["value"], "en", "bg") for x in data["ingredients"]])

@api.get("/recentRecipes")
async def recent() -> None:
    pool: PostgreSQLClient = current_app.db
    return {"results": [dict(x) for x in await pool.fetch("SELECT * FROM dishes ORDER BY timestamp DESC LIMIT 12;")]}

@api.route("/bookmarks", methods=["POST", "PUT", "DELETE"])
async def bookmarks() -> None:
    if not current_user.auth_id:
        return {
            "error": "Трябва да сте влезли в акаунта си, за да добавите това ястие към любимите ви ястия!"
        }, 401
        
    data = json.loads(await request.data)
    pool: PostgreSQLClient = current_app.db

    if request.method == "POST":
        return {"state": bool(await pool.fetchrow("SELECT * FROM bookmarks WHERE account = $1 AND dish = $2", current_user.auth_id, data.get("id")))}

    if request.method == "PUT":
        await pool.execute("INSERT INTO bookmarks(account, dish) VALUES($1, $2)", current_user.auth_id, data.get("id"))
        return "", 200

    if request.method == "DELETE":
        await pool.execute("DELETE FROM bookmarks WHERE account = $1 AND dish = $2", current_user.auth_id, data.get("id"))
        return "", 200

@api.post("/bookmarksCount")
async def bookmarksCount() -> None:
    data = json.loads(await request.data)
    return {"count": (await current_app.db.fetchrow("SELECT COUNT(*) as amount FROM bookmarks WHERE dish = $1", data.get("id")))["amount"]}
    
@api.get("/topIngredients")
async def topIngredients() -> None:
    pool: PostgreSQLClient = current_app.db
    output = {
        "labels": [],
        "data": []
    }
    
    ingr = []
    for i in [dict(x)["ingredients"] for x in await pool.fetch("SELECT ingredients FROM dishes")]:
        ingr.extend(i)

    for i in Counter(ingr).most_common(15):
        output["labels"].append(i[0])
        output["data"].append(i[1])
    return output

@api.get("/topLiked")
async def topLiked() -> None:
    pool: PostgreSQLClient = current_app.db
    output = {
        "labels": [],
        "data": []
    }
    

    for i in Counter([dict(x)["dish"] for x in await pool.fetch("SELECT dish FROM bookmarks")]).most_common(15):
        output["labels"].append(await pool.fetchval("SELECT title FROM dishes WHERE id = $1", i[0]))
        output["data"].append(i[1])
    return output

@api.get("/userTop")
@login_required
async def userTop() -> None:
    pool: PostgreSQLClient = current_app.db
    output = {
        "labels": [],
        "data": []
    }

    ingr = []
    for i in [dict(x)["ingredients"] for x in await pool.fetch(
        "SELECT * FROM dishes WHERE id IN (SELECT dish FROM bookmarks WHERE account = $1) ORDER BY timestamp DESC", 
        current_user.auth_id
    )]:
        ingr.extend(i)

    for i in Counter(ingr).most_common(15):
        output["labels"].append(i[0].split(" -")[0])
        output["data"].append(i[1])
    return output
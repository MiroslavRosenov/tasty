import json
import hashlib

from quart import Blueprint, render_template, request, current_app
from quart_auth import AuthUser, login_user

from ext.translator import Translator
from ext.base import search_tags

api = Blueprint("api", __name__, url_prefix="/api")
translate = Translator().translate

@api.post("/searchRecipe")
async def search() -> None:
    data = json.loads(await request.data)
    return await search_tags([translate(x["value"], "en", "bg") for x in data["ingredients"]])

@api.get("/recentRecipes")
async def recent() -> None:
    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        query = "SELECT title, id, imageUrl FROM details ORDER BY last_looked DESC LIMIT 12;"
        cur.execute(query)
        return {"results": cur.fetchall()}

@api.post("/signin")
async def signin() -> None:
    data = json.loads(await request.data)

    query = "SELECT * FROM accounts WHERE email = %s AND password = %s"
    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        cur.execute(query, (data.get("email"), hashlib.sha256(data.get("password").encode("utf-8")).hexdigest()))
        if not (resp := cur.fetchone()):
            return {
                "error": "Акаунтът не беше намерен"
            }, 403
        if not resp["confirmed"]:
            return {
                "error": "Моля, потвърдете акаунта си" 
            }, 403
        login_user(AuthUser(resp["id"]), data.get("remember"))
        return "", 200
        

import httpx
import os
import json

from typing import Optional, Dict, List
from quart import current_app
from quart_auth import AuthUser
from mysql.connector.cursor import MySQLCursorPrepared

from ext.cache import getter
from ext.translator import Translator

translate = Translator().translate

class User(AuthUser):
    def __init__(self, auth_id: str) -> None:
        super().__init__(auth_id)

    def get(self) -> Dict[str , any]:
        with current_app.db.cursor(dictionary=True, buffered=False) as cur:
            query = "SELECT * FROM accounts WHERE id = %s" 
            cur.execute(query, (self.auth_id,))
            resp = cur.fetchone()
            return resp

    
# @getter("recipe_by_query")
async def search_tags(ingredients: List[str]) -> Dict:
    with current_app.db.cursor(prepared=True, buffered=False) as cur:
        generated = "AND ".join(["JSON_SEARCH(ingredients, 'all', %s) IS NOT NULL " for i in range(len(ingredients))])
        query = f"SELECT * FROM dishes WHERE {generated} LIMIT 12"
 
        cur.execute(query, [translate(x) for x in ingredients])
        if (resp := cursor_to_dict(cur)) and len(resp) >= 12:
            return {"results": resp}
        
    
    resp = httpx.get(
        "https://api.spoonacular.com/recipes/findByIngredients",

        params={
            "ingredients": ",".join(ingredients),
            "apiKey": os.getenv("TOKEN"),
            "number": 8,
            "ranking": 1
        }
    )

    if resp.status_code != 200:
        return {
            "error": resp.status_code
        }
    
    if not (dishes := (resp.json())):
        return {
            "error": 404,
            "details": "Recipe not found"
        }

    with current_app.db.cursor(prepared=True, buffered=False) as cur:
        results = []

        for dish in dishes:
            cur.execute("SELECT * FROM dishes WHERE id = %s", (dish["id"],))
            if not (resp := cursor_to_dict(cur)):
                query = "INSERT INTO dishes (id, title, imageUrl, ingredients) VALUES (%s, %s, %s, %s)"
                cur.execute(
                    query, 
                    (
                        dish["id"],
                        translate(dish["title"]),
                        dish["image"],
                        json.dumps([translate(x["name"]) for x in dish["usedIngredients"] + dish["missedIngredients"]], ensure_ascii=False)
                    )
                )

                cur.execute("SELECT * FROM dishes WHERE id = %s", (dish["id"],))
                resp = cursor_to_dict(cur)
            results.append(resp)
        current_app.db.commit()
    return {"results": results[0]}

@getter("recipe_by_id")
async def get_recipe(id: int) -> Dict:
    resp = httpx.get(
        f"https://api.spoonacular.com/recipes/{id}/information",
        params={
            "includeNutrition": False,
            "apiKey": os.getenv("TOKEN"),
        }
    )

    if resp.status_code != 200:
        return {
            "error": resp.status_code
        }
    
    if not (data := (resp.json())):
        return {
            "error": 404,
            "details": "Recipe not found"
        }

    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        cur.execute("SELECT * FROM details WHERE id = %s", (data['id'],))
        if not (resp := cur.fetchone()):
            query = "INSERT INTO details (id, title, readyInMinutes, imageUrl, ingredients, instructions) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(
                query, 
                (
                    data["id"],
                    translate(data["title"]),
                    data["readyInMinutes"],
                    data["image"],
                    json.dumps([{"name": translate(x["name"]), "imageUrl": f"https://spoonacular.com/cdn/ingredients_100x100/{x['image']}"} for x in data["extendedIngredients"]], ensure_ascii=False),
                    json.dumps([{"step": translate(x["step"])} for x in data["analyzedInstructions"][0]["steps"]] if len(data["analyzedInstructions"]) != 0 else [], ensure_ascii=False)
                )
            )
            
            cur.execute("SELECT * FROM details WHERE id = %s", (data['id'],))
            resp = cur.fetchone()
        cur.execute("UPDATE details SET last_looked = NOW() WHERE id = %s", (resp["id"],))
        
        current_app.db.commit()

    resp["ingredients"] = json.loads(resp["ingredients"])
    resp["instructions"] = json.loads(resp["instructions"])
    return resp

def cursor_to_dict(cur: MySQLCursorPrepared) -> Optional[List[Dict]]:
    row_headers=[x for x in cur.column_names]

    if (data := [dict(zip(row_headers, result)) for result in cur.fetchall()]):
        return data
    return None
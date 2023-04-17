import httpx
import os
import json
import contextlib

from typing import Optional, Dict, List
from mysqlx import IntegrityError
from quart import current_app
from mysql.connector.cursor import MySQLCursorPrepared

from ext.cache import getter
from ext.translator import Translator

translate = Translator().translate

# @getter("recipe_by_tags")
async def search_tags(ingredients: List[str]) -> Dict:
    with current_app.db.cursor(prepared=True, buffered=False) as cur:
        generated = "AND ".join(["JSON_SEARCH(ingredients, 'all', %s) IS NOT NULL " for i in range(len(ingredients))])
        query = f"SELECT * FROM dishes WHERE {generated} LIMIT 12"

        cur.execute(query, [f"%{translate(x)}%" for x in ingredients])
        if (resp := cursor_to_dict(cur)):
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

        results = []

        for dish in dishes:
            cur.execute("SELECT * FROM dishes WHERE id = %s", (dish["id"],))
            if not (resp := cursor_to_dict(cur, "one")):
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
                resp = cursor_to_dict(cur, "one")
            results.append(resp)
        current_app.db.commit()
    return {"results": results}

@getter("recipe_by_id")
async def recipe_details(id: int) -> Dict:
    with current_app.db.cursor(prepared=True, buffered=False) as cur:
        cur.execute("UPDATE dishes SET timestamp = NOW() WHERE id = %s", (id,))
        query = "SELECT * FROM details WHERE id = %s"
        cur.execute(query, (id,))
        if (resp := cursor_to_dict(cur)):
            resp = resp[0]
            resp["ingredients"] = json.loads(resp["ingredients"])
            resp["instructions"] = json.loads(resp["instructions"])
            return resp

    resp = httpx.get(
        f"https://api.spoonacular.com/recipes/{id}/information",
        params={
            "includeNutrition": True,
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
        with contextlib.suppress(IntegrityError):
            query = "INSERT INTO details (id, title, readyInMinutes, imageUrl, ingredients, instructions) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(
                query, 
                (
                    data["id"],
                    translate(data["title"]),
                    data["readyInMinutes"],
                    data["image"],
                    json.dumps([{"name": translate(x["name"]), "imageUrl": f"https://spoonacular.com/cdn/ingredients_100x100/{x['image']}"} for x in data["extendedIngredients"]], ensure_ascii=False),
                    json.dumps([translate(x["step"]) for x in data["analyzedInstructions"][0]["steps"]] if len(data["analyzedInstructions"]) != 0 else [], ensure_ascii=False)
                )
            )
        
        cur.execute("SELECT * FROM details WHERE id = %s", (data['id'],))
        resp = cur.fetchone()
        
        current_app.db.commit()

    resp["ingredients"] = json.loads(resp["ingredients"])
    resp["instructions"] = json.loads(resp["instructions"])
    return resp

def cursor_to_dict(cur: MySQLCursorPrepared, strategy: str = "all") -> Optional[List[Dict]]:
    row_headers=[x for x in cur.column_names]
    data = [dict(zip(row_headers, result)) for result in cur.fetchall()] or None
    
    if strategy == "all":
        return data 
    else:
        with contextlib.suppress(TypeError):
            return data[0]

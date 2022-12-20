import httpx
import os
import json

from typing import Dict, List
from quart import current_app
from quart_auth import AuthUser

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
async def search_recipe(ingredients: List[str]) -> Dict:
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
    

    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        result = {"results": []}

        for dish in dishes:
            cur.execute("SELECT * FROM dishes WHERE id = %s", (dish["id"],))
            if not (resp := cur.fetchone()):
                query = "INSERT INTO dishes (id, title, imageUrl, ingredients) VALUES (%s, %s, %s, %s)"
                cur.execute(
                    query, 
                    (
                        dish["id"],
                        translate(dish["title"], "bg", "en"),
                        dish["image"],
                        ", ".join([translate(x["name"], "bg", "en") for x in dish["usedIngredients"] + dish["missedIngredients"]])
                    )
                )

                cur.execute("SELECT * FROM dishes WHERE id = %s", (dish["id"],))
                resp = cur.fetchone()
            result["results"].append(resp)
        current_app.db.commit()
    print("Sent!")
    return result

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
                    json.dumps([{"name": translate(x["originalName"]), "imageUrl": f"https://spoonacular.com/cdn/ingredients_100x100/{x['image']}"} for x in data["extendedIngredients"]], ensure_ascii=False),
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

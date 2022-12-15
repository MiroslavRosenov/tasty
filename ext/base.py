import httpx
import os
import json

from typing import Dict
from quart import current_app
from deep_translator import GoogleTranslator

from ext.cache import getter
from ext.translator import Translator

translate = Translator().translate
# translate = GoogleTranslator("en", "bg").translate

@getter("recipe_by_query")
async def search_recipe(query: str) -> Dict:
    resp = httpx.get(
        "https://api.spoonacular.com/recipes/search",

        params={
            "query": query,
            "apiKey": os.getenv("TOKEN"),
            "number": 9
        }
    )

    if resp.status_code != 200:
        return {
            "error": resp.status_code
        }
    
    if not (data := (resp.json()["results"])):
        return {
            "error": 404,
            "details": "Recipe not found"
        }

    with current_app.db.cursor(dictionary=True, buffered=False) as cur:
        result = {"results": []}

        for x in data:
            cur.execute(f"SELECT * FROM recipes WHERE id = {x['id']}")
            if not (resp := cur.fetchone()):
                query = "INSERT INTO recipes (id, name, original_name, readyInMinutes, imageUrl) VALUES (%s, %s, %s, %s, %s);"
                cur.execute(
                    query, 
                    (
                        x["id"],
                        translate(x["title"], "bg", "en"),
                        x["title"],
                        x["readyInMinutes"],
                        f"https://spoonacular.com/recipeImages/{x['id']}-636x393.{x['image'].split('.')[1]}"
                    )
                )

                cur.execute(f"SELECT * FROM recipes WHERE id = {x['id']}")
                resp = cur.fetchone()
            result["results"].append(resp)
        current_app.db.commit()
    return result

@getter("recipe_by_id",)
async def get_recipe(id: int) -> Dict:
    resp = httpx.get(
        f"https://api.spoonacular.com/recipes/{id}/information",
        params={
            # "includeNutrition": False,
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
        cur.execute(f"SELECT * FROM recipe_details WHERE id = {data['id']}")
        if not (resp := cur.fetchone()):
            query = "INSERT INTO recipe_details (id, name, original_name, readyInMinutes, imageUrl, ingredients, instructions) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            cur.execute(
                query, 
                (
                    data["id"],
                    translate(data["title"], "bg", "en"),
                    data["title"],
                    data["readyInMinutes"],
                    data["image"],
                    json.dumps([{"name": translate(x["originalName"], "bg", "en"), "imageUrl": f"https://spoonacular.com/cdn/ingredients_100x100/{x['image']}"} for x in data["extendedIngredients"]], ensure_ascii=False),
                    json.dumps([{"step": translate(x["step"], "bg", "en")} for x in data["analyzedInstructions"][0]["steps"]] if len(data["analyzedInstructions"]) != 0 else [], ensure_ascii=False)
                )
            )
            
            cur.execute(f"SELECT * FROM recipe_details WHERE id = {data['id']}")
            resp = cur.fetchone()
        cur.execute("UPDATE recipe_details SET last_looked = NOW() WHERE id = %s", (resp["id"],))
        
        current_app.db.commit()

    resp["ingredients"] = json.loads(resp["ingredients"])
    resp["instructions"] = json.loads(resp["instructions"])
    return resp
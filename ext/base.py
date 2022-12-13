import httpx
import os
from ext.cache import getter
from typing import Dict
from quart import current_app
from deep_translator import GoogleTranslator
from mysql.connector import cursor


translate = GoogleTranslator("en", "bg").translate

# @getter("recipe_by_query")
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
        result = {
            "results": []
        }

        for x in data:
            cur.execute(f"SELECT * FROM recipes WHERE id = {x['id']}")
            if not (resp := cur.fetchone()):
                query = "INSERT INTO recipes (id, name, readyInMinutes, image, sourceUrl) VALUES (%s, %s, %s, %s, %s);"
                cur.execute(query, (x["id"], translate(x["title"]), x["readyInMinutes"], f"https://spoonacular.com/recipeImages/{x['id']}-636x393.{x['image'].split('.')[1]}", x["sourceUrl"]))

                cur.execute(f"SELECT * FROM recipes WHERE id = {x['id']}")
                resp = cur.fetchone()

            current_app.db.commit()
            result["results"].append(resp)
    return result

# @getter("recipe_by_id",)
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

    return {
        "name": data["title"].capitalize(),
        "readyInMinutes": data["readyInMinutes"],
        "image": data["image"],
        "ingredients": [
            {
                "name": x["originalName"].capitalize(),
                "image": x['image']
            } for x in data["extendedIngredients"]
        ],
        "instructions": [
            {
                "step": x["step"]
            } for x in data["analyzedInstructions"][0]["steps"]
        ] if len(data["analyzedInstructions"]) != 0 else []
    }
import httpx
import os
from ext.cache import getter
from typing import Dict
from quart import current_app

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

    return {
        "results":[
            {
                "name": x["title"],
                "id": x["id"],
                "readyInMinutes": x["readyInMinutes"],
                "sourceUrl": x["sourceUrl"],
                "image": f"https://spoonacular.com/recipeImages/{x['id']}-636x393.{x['image'].split('.')[1]}",
            } for x in data
        ],
    }

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